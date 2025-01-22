import smtplib
from ldap3 import Server, Connection
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests
from datetime import datetime
import time
from model import Session, Tool, Record, Tool_preferences, User
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
smtp_password = ""

# LDAP setup
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
base_dn = "ou=servicegroups,dc=wikimedia,dc=org"
attributes = ["member"]
server = Server(ldap_server, use_ssl=True)
connection = Connection(server, auto_bind=True)


def get_maintainers(tool_data):
    tool_name = tool_data["name"]
    tool_name = tool_name.removeprefix("toolforge.")
    tool_name = tool_name.removeprefix("toolforge-")
    tool_name = tool_name.removeprefix("tools.")
    tool_name = tool_name.removesuffix("-")

    # Each tool belongs to an LDAP group in which the maintainers are the group members
    search_filter = f"(cn=tools.{tool_name})"
    connection.search(base_dn, search_filter, attributes=attributes)

    # Extract the UIDs (usernames) from the member attribute
    uids = []
    if connection.entries:
        for member_dn in connection.entries[0].member:
            uid = member_dn.split(",")[0].split("=")[1]
            uids.append(uid)
    return uids


def fetch_and_store_data():
    API_URL = config["API_URL"]
    response = requests.get(API_URL)
    data = response.json()

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

            maintainers = get_maintainers(tool_data)
            for maintainer in maintainers:
                user = session.query(User).filter(User.username == maintainer).first()
                if not user:
                    user = User(username=maintainer)
                    session.add(user)

                tool_preferences = (
                    session.query(Tool_preferences)
                    .filter(Tool_preferences.user == user, Tool_preferences.tool == tool)
                    .first()
                )
                if not tool_preferences:
                    tool_preferences = Tool_preferences(user=user, tool=tool)
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
            tool_pref = session.query(Tool_preferences).filter(Tool_preferences.tool_id == tool.id).first()
            last_up = (
                session.query(Record)
                .filter(and_(Record.tool_id == tool.id, Record.health_status == True))
                .order_by(desc(Record.timestamp))
                .first()
            )

            if last_up is not None and tool_pref.send_email and tool_pref.interval != 0:
                # Since the cron job runs every 30 minutes, first time it went down will be 30 minutes + last time it was up.
                if tool_pref.interval * 60 <= ((datetime.now() - last_up.timestamp).total_seconds() + 1800):
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
    body = (
        f"Your tool: {tool_name} went down at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nYou are receiving this message because you have opted in to receive email notifications when your tool goes down on https://tool-watch.toolforge.org/",
    )

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(smtp_user, smtp_password)  # Login to the server
            server.sendmail(smtp_user, to_email, msg.as_string())  # Send the email
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
