import smtplib
from ldap3 import Server, Connection, RESTARTABLE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests
from datetime import datetime
import time
from model import Session, Tool, Record, ToolPreferences, Maintainer
from config import config
from sqlalchemy import create_engine, desc, and_
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse

load_dotenv()

# Email setup
page_limit = config["page_limit"]
smtp_host = "mail.tools.wmcloud.org"
smtp_port = 587
smtp_user = "tool-watch.alerts@toolforge.org"


def setup_ldap():
    try:
        with open("/etc/ldap.conf") as file:
            for line in file.readlines():
                if "uri" in line:
                    ldap_server = line.split()[1]
    except FileNotFoundError:
        print("/etc/ldap.conf not found, assuming local development environment")
        # Ensure that you have an SSH tunnel to the LDAP server:
        # ssh -N <login>@dev.toolforge.org -L 3389:ldap-ro.eqiad.wikimedia.org:389
        ldap_server = "ldap://localhost:3389"

    server = Server(ldap_server, use_ssl=True)
    connection = Connection(server, client_strategy=RESTARTABLE, auto_bind=True)
    return connection


def get_maintainers(tool_data, ldap_connection):
    base_dn = "ou=people,dc=wikimedia,dc=org"
    attributes = ["uid", "wikimediaGlobalAccountName"]

    tool_name = tool_data["name"]
    tool_name = tool_name.removeprefix("toolforge.")
    tool_name = tool_name.removeprefix("toolforge-")
    tool_name = tool_name.removeprefix("tools.")
    tool_name = tool_name.removesuffix("-")

    # Each maintainer is a member of the group that the tool belongs to
    search_filter = f"(memberOf=cn=tools.{tool_name},ou=servicegroups,dc=wikimedia,dc=org)"
    ldap_connection.search(base_dn, search_filter, attributes=attributes)

    uids = []
    if ldap_connection.entries:
        for entry in ldap_connection.entries:
            # Prefer the SUL username if present since OAuth returns SUL
            uid = entry.wikimediaGlobalAccountName.value or entry.uid.value
            uids.append(uid)
    return uids


def fetch_and_store_data():
    API_URL = config["API_URL"]
    headers = {'User-Agent':'toolwatch/1.0 requests/flask'}
    response = requests.get(API_URL, headers=headers)
    print(response.status_code)
    print(response.text)
    data = response.json()
    ldap_conn = setup_ldap()

    session = Session()
    total_pages = len(data) // page_limit
    for page in range(1, total_pages + 1):
        start = (page - 1) * page_limit
        end = page * page_limit
        page_data = data[start:end]

        for tool_no, tool_data in enumerate(page_data):
            tool = session.query(Tool).filter(Tool.name == tool_data["name"]).first()

            if tool:
                tool.web_tool = tool_data.get("tool_type") == "web app"
            else:
                tool = Tool(
                    name=tool_data["name"],
                    title=tool_data["title"],
                    description=tool_data["description"],
                    url=tool_data["url"],
                    keywords=tool_data.get("keywords", ""),
                    author=tool_data["author"][0]["name"],
                    repository=tool_data.get("repository", ""),
                    license=tool_data.get("license", ""),
                    technology_used=", ".join(tool_data.get("technology_used", [])),
                    bugtracker_url=tool_data.get("bugtracker_url", ""),
                    page_num=page,
                    total_pages=total_pages,
                    web_tool=tool_data.get("tool_type") == "web app",
                )
                session.add(tool)

            maintainers = get_maintainers(tool_data, ldap_conn)
            for maintainer in maintainers:
                user = session.query(Maintainer).filter(Maintainer.username == maintainer).first()
                if not user:
                    user = Maintainer(username=maintainer)
                    session.add(user)
                if user not in tool.maintainers:
                    tool.maintainers.append(user)

                tool_preferences = (
                    session.query(ToolPreferences)
                    .filter(ToolPreferences.user == user, ToolPreferences.tool == tool)
                    .first()
                )
                if not tool_preferences:
                    tool_preferences = ToolPreferences(user=user, tool=tool)
                    session.add(tool_preferences)
            print(f"Finished inserting tool: {start + tool_no}/{len(data)}")

        session.commit()
    session.close()


def sync_get(url):
    try:
        print(f"[*] Fetching url {url}")
        response = requests.head(url, timeout=5)
        if response.status_code >= 200 and response.status_code < 399:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def ping_every_30_minutes():
    engine = create_engine(config["MARIADB_URI"])
    SessionInit = sessionmaker(bind=engine)
    session = SessionInit()
    # Fetch all tools from the database, excluding the ones that are not web tools
    tools = session.query(Tool).filter(Tool.web_tool == True).all()
    print("Checking health status of tools")
    for tool in tools:
        url = tool.url
        time.sleep(0.01)
        url_parsed = urlparse(url)
        print(f"[*] Checking health of {url} with hostname {url_parsed.hostname}")
        if url_parsed.hostname is not None and "toolforge.org" in url_parsed.hostname:
            result = sync_get(url)
        else:
            result = False  # Don't check the health of non-toolforge.org urls
        print(f"[*] {url} is {result}")
        tool.health_status = result
        tool.last_checked = datetime.now()
        record = Record(tool=tool, health_status=result)
        session.add(tool)
        session.add(record)
        session.commit()

        if tool.health_status is False:
            tool_pref = session.query(ToolPreferences).filter(ToolPreferences.tool_id == tool.id).first()
            if not tool_pref:  # lack of ToolPreference implies that the tool has no maintainer
                continue

            last_up = (
                session.query(Record)
                .filter(and_(Record.tool_id == tool.id, Record.health_status == True))
                .order_by(desc(Record.timestamp))
                .first()
            )

            if last_up is not None and tool_pref.send_email and tool_pref.interval != 0:
                # Since the cron job runs every 24 hours, the tool's downtime will be detected in the next crawl after it was last seen up
                # Hence the effective downtime is (now−last_up) − 24h/86,400s
                if ((datetime.now() - last_up.timestamp).total_seconds() - 86400) >= tool_pref.interval * 86400:
                    try:
                        name = tool_pref.tool.name
                        if "toolforge." in name:
                            name = name.split("toolforge.")[-1]
                        elif "toolforge-" in name:
                            name = name.split("toolforge-")[-1]
                        send_email(name)
                        tool_pref.send_email = False
                        session.commit()

                    except Exception as e:
                        print("Failed to send mail!", e)


def send_email(tool_name):
    to_email = f"{tool_name}.notifications@toolforge.org"
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"Your Wikimedia Tool: {tool_name} is down!"
    body = f"Your tool: {tool_name} went down at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nYou are receiving this message because you have opted in to receive email notifications when your tool goes down on https://tool-watch.toolforge.org/"

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Upgrade to secure connection
            server.sendmail(smtp_user, to_email, msg.as_string())  # Send the email
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
