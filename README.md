# ToolWatch Status Application

ToolWatch checks the health status of various tools and displays them in a user-friendly UI.
More at: https://phabricator.wikimedia.org/T341379

## Installation

1. Clone the repository: `git clone https://github.com/gopavasanth/ToolWatch`
2. Navigate to the project directory: `cd ToolWatch`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - For Windows: `venv\Scripts\activate`
   - For Unix/Linux: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`

## Usage

1. Run the Flask app: `python app.py`
2. Open your web browser and visit `http://localhost:5000` to view the tool health status.

## Directory Structure

The directory structure of the project is as follows:

- The `database` directory contains the SQLite database file.
- The `tools` directory contains the application code for tools.
  - The `templates` directory contains HTML templates.
  - The `models.py` file defines the Tool model and sets up the database.
  - The `views.py` file contains the Flask routes and logic.
  - The `__init__.py` file initializes the tools blueprint.
- The `main.py` file is the main entry point of the Flask application.

## Customization

- To add or modify tools, you can edit the `tools/models.py` file and add or update the Tool model attributes.
- For more advanced health checks, you can modify the `tools/views.py` file and implement the logic in the `check_tool_health()` function.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
