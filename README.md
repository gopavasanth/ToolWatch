# ToolWatch Status Application

ToolWatch checks the health status of various Wikimedia tools and displays them in a user-friendly UI.
More at: https://phabricator.wikimedia.org/T341379

## Installation

1. Clone the repository: `git clone https://github.com/gopavasanth/ToolWatch`
2. Navigate to the project directory: `cd ToolWatch`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - For Windows: `venv\Scripts\activate`
   - For Unix/Linux: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`

## Database

1. Before starting the app, you need to start the MariaDB instance on your local device.
2. You can install the MariaDB from [here](https://mariadb.com/downloads/), or other sources.
3. After installing the MariaDB, you need to create a database with the following credentials:

   - database name: `toolwatch`
   - username: `root`
   - password: `toolwatch`

4. These credentials are defined in `config.py` file.

> _For production, we use Wikimedia Cloud database, and for production purposes we may need to create a .env file, with variables defined._

## Usage

1. Run the database service (MariaDB instance, if running locally).
2. Run the Flask app: `python app.py`
3. Open your web browser and visit `http://localhost:5000` to view the tool health status.

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
