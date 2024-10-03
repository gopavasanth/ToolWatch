# ToolWatch Status Application

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

### Create the `toolwatch` Database and User in MariaDB

**a. Log into MariaDB as the Root User**

First, you need to access the MariaDB server using the root account. Open your terminal and execute:

```bash
sudo mysql -u root -p
```

You'll be prompted to enter the root password. If you haven't set one yet, you might need to secure your MariaDB installation first.

**b. Create the `toolwatch` Database**

Once you're logged in, create the new database:

```sql
CREATE DATABASE toolwatch;
```

**c. Create a New User `toolwatch` with Password `toolwatch`**

It's a best practice **not** to use the `root` user for your applications. Instead, create a dedicated user with specific privileges:

```sql
CREATE USER 'toolwatch'@'localhost' IDENTIFIED BY 'toolwatch';
```

**d. Grant All Privileges on the `toolwatch` Database to the `toolwatch` User**

Assign the necessary permissions to the newly created user:

```sql
GRANT ALL PRIVILEGES ON toolwatch.* TO 'toolwatch'@'localhost';
```

**e. Apply the Changes**

Ensure that MariaDB reloads the privilege tables to recognize the new user and permissions:

```sql
FLUSH PRIVILEGES;
```

**f. Exit MariaDB**

```sql
EXIT;
```

**g. Open `config.py` in your preferred text editor and update the user name to `toolwatch`**

> _For production, we use Wikimedia Cloud database, and for production purposes we may need to create a .env file, with variables defined._

## Usage

1. Run the database service (MariaDB instance, if running locally).
2. After setting it up locally, run the cron.py file: `python cron.py`, which is scheduled to run automatically every 24 hours, manually execute it once to trigger the data crawling process. The run should take approximately 45 minutes to complete.
3. Run the Flask app: `python app.py`
4. Open your web browser and visit `http://localhost:5000` to view the tool health status.

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
