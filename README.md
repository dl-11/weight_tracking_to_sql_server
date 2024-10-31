# Weight Tracking to SQL

A Python-based weight tracking application that allows users to record their weight, sleep duration, resting heart rate, and notes. It also provides data visualization, statistics, and weight prediction using linear regression.

## Features

- **Add Weight Entry**: Record daily weight along with sleep duration, resting heart rate, and personal notes.
- **Update Weight Entry**: Modify existing entries in the database.
- **View Weight Log**: Display all recorded entries.
- **Visualize Data**: Generate graphs for weight, sleep duration, and resting heart rate over time.
- **Calculate Statistics**: Compute average, minimum, maximum weights, and weight changes over time.
- **Predict Future Weight**: Forecast weight for the next 30 days using linear regression.
- **Backup and Restore Data**: Save and load data to/from a CSV file.
- **Import and Export Data**: Import data from or export data to a CSV file.

## Installation

1. **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/dl-11/weight_tracking_to_sql_server
   cd weight_tracking_to_sql_server
   ```

2. **Set Up a Virtual Environment** (Optional but Recommended)

   Create and activate a virtual environment to isolate the project's dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install ODBC Driver for SQL Server**

   The application uses `pyodbc` to connect to a SQL Server database. You need to install the ODBC driver:

   - **For Ubuntu Linux:**

     ```bash
     # Import the public repository GPG keys
     curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

     # Register the Microsoft Ubuntu repository
     sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list)"

     # Update the package list and install the ODBC driver
     sudo apt-get update
     sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

     # Optional: Install unixODBC development headers if needed
     sudo apt-get install -y unixodbc-dev
     ```

   - **For Other Operating Systems:**

     Refer to the [Microsoft documentation](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server) for installation instructions specific to your OS.

5. **Set Up Environment Variables**

   The application requires certain environment variables to connect to your database. Set them in your shell or add them to your shell profile (`.bashrc`, `.bash_profile`, or `.zshrc`):

   ```bash
   export DB_HOST=your_db_host         # Optional, defaults to 192.168.1.1 if not set
   export WTDB_NAME=your_database_name # Name of your database
   export DB_USER=your_database_user   # Your database username
   export DB_PASSWORD=your_password    # Your database password
   ```

   - **Example:**

     ```bash
     export DB_HOST=192.168.1.1
     export WTDB_NAME=weight_tracker_database
     export DB_USER=user
     export DB_PASSWORD=yourStrong(!)Password
     ```

6. **Ensure Database Connectivity**

   - **Create the Database:**

     If your database does not exist, you need to create it in your SQL Server instance.

     ```sql
     CREATE DATABASE your_database_name;
     ```

   - **Grant Permissions:**

     Ensure that the user specified in the environmental variables has the necessary permissions to connect to the database and create tables.

   - **Test Connection:**

     You can test the database connection using a simple Python script or command-line tool to ensure that the connection parameters are correct.

## Usage

Run the application from the command line:

```bash
python weight_tracking_to_sql.py
```

You will see the interactive menu:

```
--- Weight Tracker Menu ---
1. Add weight entry
2. Visualize weight data
3. View weight log
4. Calculate statistics
5. Update weight entry
6. Predict future weight
7. Backup data
8. Restore data
9. Export data
10. Import data
11. Exit
Choose an option (1-11):
```

### Menu Options

1. **Add Weight Entry**

   - Follow the prompts to enter:
     - **Date**: In `YYYY-MM-DD` format.
     - **Weight**: In pounds (leave blank if unknown).
     - **Notes**: Any additional notes (optional).
     - **Sleep Duration**: Hours slept (optional).
     - **Resting Heart Rate**: In beats per minute (optional).

2. **Visualize Weight Data**

   - Generates graphs for:
     - Weight over time.
     - Sleep duration over time.
     - Resting heart rate over time.
     - Sleep duration vs. resting heart rate.

3. **View Weight Log**

   - Displays all recorded entries with details.

4. **Calculate Statistics**

   - Provides statistical insights:
     - Average, minimum, and maximum weights.
     - Total and average daily weight change.
     - Resting heart rate statistics.
     - Weight change by month.

5. **Update Weight Entry**

   - Allows you to update an existing entry by date.

6. **Predict Future Weight**

   - Uses linear regression to predict weight for the next 30 days.

7. **Backup Data**

   - Saves your data to `weight_data_backup.csv`.

8. **Restore Data**

   - Restores data from `weight_data_backup.csv`.

9. **Export Data**

   - Exports your data to `weight_data_export.csv`.

10. **Import Data**

    - Imports data from `weight_data_import.csv`.

11. **Exit**

    - Closes the application and the database connection.

## Requirements

- **Python**: Version 3.6 or higher.
- **Database**: SQL Server accessible via ODBC.
- **ODBC Driver**: Appropriate driver installed for SQL Server.
- **Environment Variables**: `DB_HOST`, `WTDB_NAME`, `DB_USER`, and `DB_PASSWORD`.

## Dependencies

All dependencies are listed in `requirements.txt`:

- `pyodbc`
- `matplotlib`
- `pandas`
- `numpy`
- `scikit-learn`

Install them using:

```bash
pip install -r requirements.txt
```

## Files Included

- `weight_tracking_to_sql.py`: Main application code.
- `requirements.txt`: List of Python dependencies.
- `.gitignore`: Specifies files to ignore in the repository.
- `README.md`: Project documentation (this file).
- `LICENSE`: License information.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear commit messages.
4. Push your branch to your forked repository.
5. Submit a pull request describing your changes.

## License

This project is licensed under the **MIT License**. See the license file for details.

## Additional Notes

- **Database Initialization**

  - The application automatically creates the `Weights` table if it doesn't exist.
  - Ensure that your database user has permissions to create tables.

- **Error Handling**

  - The application includes error handling for invalid inputs and database exceptions.
  - In case of errors, descriptive messages will guide you to resolve them.

- **Data Privacy**

  - Be cautious with your database credentials.
  - Do not commit sensitive information like passwords to version control.
  - Use environment variables or configuration files excluded from version control to manage sensitive data.

- **Environment Variables Example**

  To make environmental variables persistent, add them to your shell profile (`~/.bashrc`, `~/.bash_profile`, or `~/.zshrc`).

- **Running Without Environment Variables**

  If you prefer not to use environment variables, you can modify the `weight_tracking_to_sql.py` script to include your database credentials directly. However, this is not recommended for security reasons.

- **Customizing the Application**

  - You can modify the code to add more features or adjust existing ones.
  - Ensure you comply with the license terms when distributing modified versions.

## Troubleshooting

- **ODBC Driver Issues**

  - Ensure that the ODBC driver is correctly installed and configured.
  - Verify that the driver version matches the one specified in the code (`ODBC Driver 17 for SQL Server`).

- **Database Connection Errors**

  - Double-check your environment variables for typos.
  - Ensure that the database server is running and accessible.
  - Check firewall settings that might block the connection.

- **Missing Dependencies**

  - If you encounter `ModuleNotFoundError`, ensure all dependencies are installed.
  - Use `pip list` to verify installed packages.

- **Permission Denied Errors**

  - Ensure you have read/write permissions for the project directory.
  - Run the application with appropriate user privileges.
