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


## Production

### Connect to DB Instance

To connect to the production DB instance, use the following command:

```sh
ssh -L:3307:tools.db.svc.wikimedia.cloud:3306 gopavasanth@login.toolforge.org
```

### Backup
To backup the database, run:

```sh
mariadb-dump --defaults-file=$(pwd)/replica.my.cnf --skip-ssl -h 0.0.0.0 -P 3307 s55491__toolwatch > backup.sql
```

### Jobs
* View job logs:

```sh
toolforge jobs logs -f special-restart-crawl
```

* List of jobs:

```sh
toolforge jobs list
```

### Restart Toolforge web services:

```sh
toolforge webservices restart
```

### Debug Production Container Locally

To debug the production container in local, run:

```sh
docker run -ti -u 0 --entrypoint bash tools-harbor.wmcloud.org/tool-tool-watch/tool-tool-watch:latest
```

### Grafana Monitoring
Access the Grafana dashboard https://grafana.wmcloud.org/d/TJuKfnt4z/kubernetes-namespace?orgId=1&var-cluster=prometheus-tools&var-namespace=tool-tool-watch


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

## License

This project is licensed under the [MIT License](LICENSE).
