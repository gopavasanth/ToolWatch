# ToolWatch

ToolWatch checks the health status of various Wikimedia tools and displays them in a user-friendly UI.
More at: https://phabricator.wikimedia.org/T341379

## Toolforge

To update the tool, the following commands need to be run

```sh
cd ToolWatch && git pull && ./scripts/toolforge-update.sh
```

## Installation

1. Clone the repository: `git clone https://github.com/gopavasanth/ToolWatch`
2. Navigate to the project directory: `cd ToolWatch`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - For Windows: `venv\Scripts\activate`
   - For Unix/Linux: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`

## Usage

### Database

1. Before starting the app, you need to start the MariaDB instance on your local device.
2. You can install the MariaDB from [here](https://mariadb.com/downloads/), or other sources.
3. After installing the MariaDB, you need to create a database with the following credentials:

   - database name: `toolwatch`
   - username: `root`
   - password: `toolwatch`

4. These credentials are defined in `config.py` file.

> _For production, we use Wikimedia Cloud database, and for production purposes we may need to create a .env file, with variables defined._

### Starting the app

1. Run the database service (MariaDB instance, if running locally).
2. Run the Flask app: `python app.py`
3. Open your web browser and visit `http://localhost:5000` to view the tool health status.

### Using Production Data

To connect to the production DB instance, use the following command:

```sh
ssh -L:3307:tools.db.svc.wikimedia.cloud:3306 gopavasanth@login.toolforge.org
```

This will setup an SSH tunnel to the production database.


## Directory Structure

The directory structure of the project is as follows:

- The `database` directory contains the SQLite database file.
  - The `templates` directory contains HTML templates.
  - The `model.py` file defines the Tool model and sets up the database.
- The `app.py` file is the main entry point of the Flask application.

## Customization

- To add or modify tools, you can edit the `tools/models.py` file and add or update the Tool model attributes.
- For more advanced health checks, you can modify the `tools/views.py` file and implement the logic in the `check_tool_health()` function.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.


## Maintainers Section

### Dashboards

Kubernetes: https://k8s-status.toolforge.org/namespaces/tool-tool-watch/<br>
Grafana: https://grafana.wmcloud.org/d/TJuKfnt4z/kubernetes-namespace?orgId=1&var-cluster=prometheus-tools&var-namespace=tool-tool-watch

### Connecting to prod env

```
ssh <username>@login.toolforge.org
become tool-watch
```

### Connecting to production DB

First connect to prod env using the above command, then run:

```
mariadb --defaults-file=$HOME/replica.my.cnf -h tools.db.svc.wikimedia.cloud
```

The replica.my.cnf file (present in toolforge vm) should contain:

1. DB_USER
2. DB_PASSWORD

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/ToolsDB#Steps_to_create_a_user_database

Check for <user>__toolwatchDB <- this is the production DB name.

### Backup DB

To backup the database, run:
                                 
```sh
mariadb-dump --defaults-file=$(pwd)/replica.my.cnf --skip-ssl -h 0.0.0.0 -P 3307 s55491__toolwatch > backup.sql
```

### Deployment

```
ssh <username>@login.toolforge.org
become tool-watch
```

For creating new venv

1. Delete the existing venv folder (inside /ToolWatch)

2. Log into the current kubernetes shell (powered by webservice)

```
webservice --backend=kubernetes python3.11 shell
```

3. Inside the shell, create a new venv

```
$HOME/pyvenv/bin/python3 -m venv venv
```

For installing new package, run the following command inside the kubernetes shell:

```
pip install -r requirements.txt
```

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python#Creating_a_virtual_environment

#### Webservice (Django app) Deployment

1. Build the docker image

```
toolforge build start https://github.com/gopavasanth/ToolWatch
```

> Note: To be changed with gitlab repo link once migrated.

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/Building_container_images#Build_and_deploy

2. Re-run the webservice

```
toolforge webservices restart
```

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/Building_container_images#Webservice

In case the previous instance of webservice is not running, run:

```
toolforge webservices start
```

To check the status of webservice, run:

```
toolforge webservices status
```

#### Crawler Job Deployment
First update the kubernetes cluster with the updated code. Job pod is dependent on webservice pod, so make sure webservice pod is up and running.

Create the job using:
```sh
toolforge jobs run periodic-crawl --command "daily_crawl" --image "tool-tool-watch/tool-tool-watch:latest" --schedule "@daily" --mount=all --emails=onfailure
```
The above creates a cron-job that runs the fetches the status of the tools every day.


### Debugging
- To debug the production container locally, run:

```sh
docker run -ti -u 0 --entrypoint bash tools-harbor.wmcloud.org/tool-tool-watch/tool-tool-watch:latest
```

- View job logs:

```sh
toolforge jobs logs -f special-restart-crawl
```

- List of jobs:

```sh
toolforge jobs list
```

- Restart Toolforge web services:

```sh
toolforge webservices restart
```

#### Logs
If the job fails, check the logs using

```
toolforge jobs logs <job name>
```

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/Running_jobs#Job_logs

OR

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/Running_jobs#Showing_information_about_your_job

Check for Hints section in `toolforge jobs show <job name>` to get the reason for failure.

Restart the job (post deploying webservice) using

```
toolforge jobs restart <job name>
```

Ref link: https://wikitech.wikimedia.org/wiki/Help:Toolforge/Running_jobs#Restarting_your_jobs

## License

This project is licensed under the [MIT License](LICENSE).
