import pyodbc
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import statistics
import numpy as np
import pandas as pd
from collections import defaultdict
import os

class WeightTracker:
    def __init__(self):
        """
        Initialize the WeightTracker application.

        - Reads database connection parameters from environment variables.
        - Establishes a connection to the SQL Server database.
        - Calls create_table() to ensure the Weights table exists.
        """
        # Get database parameters from environment variables
        db_host = os.environ.get('DB_HOST', '192.168.1.1')
        wtdb_name = os.environ.get('WTDB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')

        # Check that required variables are set
        if not all([wtdb_name, db_user, db_password]):
            raise ValueError("WTDB_NAME, DB_USER, and DB_PASSWORD environment variables must be set.")

        # Initialize the SQL Server connection
        self.conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={db_host};'
            f'DATABASE={wtdb_name};'
            f'UID={db_user};'
            f'PWD={db_password};'
            'Trusted_Connection=no;'
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Create the Weights table in the database if it doesn't exist.
        """
        self.cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Weights' AND xtype='U')
        BEGIN
            CREATE TABLE Weights (
                Date DATE NOT NULL PRIMARY KEY,
                Weight FLOAT NULL,
                Notes VARCHAR(50) NULL,
                WeightTrend VARCHAR(25) NULL,
                SleepDrtn FLOAT NULL,
                RestingHr INT NULL
            );
        END
        ''')
        self.conn.commit()

    def validate_date(self, date_str):
        """
        Validate date input.

        Args:
            date_str (str): Date string entered by the user.

        Returns:
            datetime.date or None: Validated date or None if invalid.
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD.")
            return None

    def validate_float(self, value_str, field_name):
        """
        Validate float inputs like weight and sleep duration.

        Args:
            value_str (str): Value string entered by the user.
            field_name (str): Name of the field for error messages.

        Returns:
            float or None: Validated float or None if invalid.
        """
        try:
            value = float(value_str)
            if value < 0:
                print(f"{field_name} cannot be negative. Please re-enter.")
                return None
            return value
        except ValueError:
            print(f"Invalid {field_name}. Please enter a number.")
            return None

    def validate_int(self, value_str, field_name):
        """
        Validate integer inputs like resting heart rate.

        Args:
            value_str (str): Value string entered by the user.
            field_name (str): Name of the field for error messages.

        Returns:
            int or None: Validated integer or None if invalid.
        """
        try:
            value = int(value_str)
            if value < 0:
                print(f"{field_name} cannot be negative. Please re-enter.")
                return None
            return value
        except ValueError:
            print(f"Invalid {field_name}. Please enter a whole number.")
            return None

    def add_weight_entry(self):
        """
        Add a new weight entry to the database.
        """
        # Gather and validate weight entry data from the user
        while True:
            date_str = input("Enter the date (YYYY-MM-DD): ")
            date = self.validate_date(date_str)
            if date:
                break

        while True:
            weight_str = input("Enter your weight in pounds (or leave blank if unknown): ")
            if weight_str == "":
                weight = None  # Allow weight to be NULL
                break
            weight = self.validate_float(weight_str, "Weight")
            if weight is not None:
                break

        notes = input("Notes (optional): ")

        while True:
            sleep_duration_str = input("Sleep duration (hours, optional): ")
            if sleep_duration_str == "":
                sleep_duration = None  # Allow sleep duration to be NULL
                break
            sleep_duration = self.validate_float(sleep_duration_str, "Sleep duration")
            if sleep_duration is not None:
                break

        while True:
            resting_hr_str = input("Resting heart rate (optional): ")
            if resting_hr_str == "":
                resting_hr = None  # Allow resting HR to be NULL
                break
            resting_hr = self.validate_int(resting_hr_str, "Resting heart rate")
            if resting_hr is not None:
                break

        # Determine weight trend based on previous entry
        weight_trend = self.calculate_weight_trend(weight)

        # Insert data into SQL Server
        try:
            self.cursor.execute('''
            INSERT INTO Weights (Date, Weight, Notes, WeightTrend, SleepDrtn, RestingHr)
            VALUES (?, ?, ?, ?, ?, ?);
            ''', (date, weight, notes, weight_trend, sleep_duration, resting_hr))
            self.conn.commit()
            print("Weight entry added successfully!")
        except Exception as e:
            print(f"Error adding entry: {e}")

    def update_weight_entry(self):
        """
        Update an existing weight entry in the database.
        """
        # Get the date for the entry to update
        while True:
            date_str = input("Enter the date of the entry to update (YYYY-MM-DD): ")
            date = self.validate_date(date_str)
            if date:
                break

        # Check if the entry exists
        self.cursor.execute("SELECT * FROM Weights WHERE Date = ?", (date,))
        result = self.cursor.fetchone()

        if not result:
            print(f"No entry found for the date {date}.")
            return

        # Display current data
        print(f"Current entry for {date}:")
        weight_display = f"{result.Weight} lbs" if result.Weight is not None else "No weight"
        print(f"Weight: {weight_display}, Notes: {result.Notes}, Trend: {result.WeightTrend}, "
              f"Sleep Duration: {result.SleepDrtn} hours, Resting HR: {result.RestingHr} bpm")

        # Ask the user what they want to update
        while True:
            weight_str = input(f"Enter new weight in pounds (current: {weight_display}) or leave blank to keep: ")
            if weight_str == "":
                weight = result.Weight  # Keep the current weight
                break
            weight = self.validate_float(weight_str, "Weight")
            if weight is not None:
                break

        notes = input(f"Enter new notes (current: {result.Notes}) or leave blank to keep: ") or result.Notes

        while True:
            sleep_duration_str = input(f"Enter new sleep duration (current: {result.SleepDrtn} hours) or leave blank to keep: ")
            if sleep_duration_str == "":
                sleep_duration = result.SleepDrtn  # Keep the current sleep duration
                break
            sleep_duration = self.validate_float(sleep_duration_str, "Sleep duration")
            if sleep_duration is not None:
                break

        while True:
            resting_hr_str = input(f"Enter new resting heart rate (current: {result.RestingHr} bpm) or leave blank to keep: ")
            if resting_hr_str == "":
                resting_hr = result.RestingHr  # Keep the current resting heart rate
                break
            resting_hr = self.validate_int(resting_hr_str, "Resting heart rate")
            if resting_hr is not None:
                break

        # Determine weight trend based on the updated weight
        weight_trend = self.calculate_weight_trend(weight)

        # Update the entry in SQL Server
        try:
            self.cursor.execute('''
            UPDATE Weights
            SET Weight = ?, Notes = ?, WeightTrend = ?, SleepDrtn = ?, RestingHr = ?
            WHERE Date = ?;
            ''', (weight, notes, weight_trend, sleep_duration, resting_hr, date))
            self.conn.commit()
            print(f"Entry for {date} updated successfully!")
        except Exception as e:
            print(f"Error updating entry: {e}")

    def calculate_weight_trend(self, current_weight):
        """
        Calculate the weight trend based on the current and previous weight.

        Args:
            current_weight (float): The current weight entered by the user.

        Returns:
            str: The weight trend ('increasing', 'decreasing', 'stable', etc.).
        """
        # If no weight was provided, we can't determine a trend
        if current_weight is None:
            return "No weight provided"

        # Fetch the most recent previous weight entry from the database
        self.cursor.execute("SELECT TOP 1 Weight FROM Weights WHERE Weight IS NOT NULL ORDER BY Date DESC")
        result = self.cursor.fetchone()

        if result is None or result.Weight is None:
            # No previous weight entries, so no trend can be determined
            return "No trend"

        previous_weight = result.Weight

        # Determine trend based on comparison with previous weight
        if current_weight > previous_weight:
            return "increasing"
        elif current_weight < previous_weight:
            return "decreasing"
        else:
            return "stable"

    def visualize_weight_data(self):
        """
        Visualize weight, sleep duration, and resting heart rate data over time.
        """
        # Fetch all relevant data for visualization
        self.cursor.execute("SELECT Date, Weight, SleepDrtn, RestingHr FROM Weights ORDER BY Date")
        data = self.cursor.fetchall()

        if not data:
            print("No data to visualize.")
            return

        dates = [row.Date for row in data]
        weights = [row.Weight for row in data]
        sleep_durations = [row.SleepDrtn for row in data]
        resting_hrs = [row.RestingHr for row in data]

        # Convert None values to NaN for plotting
        weights = [np.nan if w is None else w for w in weights]
        sleep_durations = [np.nan if s is None else s for s in sleep_durations]
        resting_hrs = [np.nan if r is None else r for r in resting_hrs]

        # Plot weight data
        plt.figure(figsize=(10, 8))

        plt.subplot(3, 1, 1)
        plt.plot(dates, weights, marker='o', label="Weight (lbs)")
        plt.ylabel("Weight (lbs)")
        plt.title("Weight Tracking Over Time")
        plt.grid(True)

        # Plot sleep duration
        plt.subplot(3, 1, 2)
        plt.plot(dates, sleep_durations, marker='o', color="orange", label="Sleep Duration (hrs)")
        plt.ylabel("Sleep Duration (hrs)")
        plt.title("Sleep Duration Over Time")
        plt.grid(True)

        # Plot resting heart rate
        plt.subplot(3, 1, 3)
        plt.plot(dates, resting_hrs, marker='o', color="green", label="Resting HR (bpm)")
        plt.ylabel("Resting HR (bpm)")
        plt.title("Resting Heart Rate Over Time")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

        # Plot Sleep vs Resting HR
        plt.figure(figsize=(8, 6))
        plt.scatter(sleep_durations, resting_hrs, color="purple")
        plt.xlabel("Sleep Duration (hrs)")
        plt.ylabel("Resting HR (bpm)")
        plt.title("Sleep Duration vs Resting Heart Rate")
        plt.grid(True)
        plt.show()

    def view_weight_log(self):
        """
        Display all weight entries in the database.
        """
        # Fetch and display all weight entries
        self.cursor.execute("SELECT * FROM Weights ORDER BY Date")
        result = self.cursor.fetchall()

        if not result:
            print("No weight entries found.")
        else:
            for entry in result:
                weight_display = f"{entry.Weight} lbs" if entry.Weight is not None else "No weight"
                print(f"Date: {entry.Date}, Weight: {weight_display}, Notes: {entry.Notes}, Trend: {entry.WeightTrend}, "
                      f"Sleep Duration: {entry.SleepDrtn} hours, Resting HR: {entry.RestingHr} bpm")

    def calculate_statistics(self):
        """
        Calculate and display statistical data from weight entries.
        """
        # Fetch weight data to calculate statistics
        self.cursor.execute("SELECT Date, Weight, RestingHr FROM Weights WHERE Weight IS NOT NULL ORDER BY Date")
        data = self.cursor.fetchall()
        if not data:
            print("No weight data available for statistics.")
            return

        dates = [entry.Date for entry in data]
        weights = [entry.Weight for entry in data]
        resting_hrs = [entry.RestingHr for entry in data if entry.RestingHr is not None]

        avg_weight = statistics.mean(weights)
        min_weight = min(weights)
        max_weight = max(weights)
        total_entries = len(weights)
        total_days = (dates[-1] - dates[0]).days or 1  # Avoid division by zero

        total_weight_change = weights[-1] - weights[0]
        average_daily_change = total_weight_change / total_days

        print(f"Average Weight: {avg_weight:.2f} lbs")
        print(f"Minimum Weight: {min_weight:.2f} lbs")
        print(f"Maximum Weight: {max_weight:.2f} lbs")
        print(f"Total Entries with Weight: {total_entries}")
        print(f"Total Weight Change: {total_weight_change:.2f} lbs")
        print(f"Average Daily Weight Change: {average_daily_change:.4f} lbs/day")

        # Resting heart rate analysis
        if resting_hrs:
            avg_resting_hr = statistics.mean(resting_hrs)
            min_resting_hr = min(resting_hrs)
            max_resting_hr = max(resting_hrs)
            print(f"Average Resting Heart Rate: {avg_resting_hr:.2f} bpm")
            print(f"Minimum Resting Heart Rate: {min_resting_hr} bpm")
            print(f"Maximum Resting Heart Rate: {max_resting_hr} bpm")
        else:
            print("No resting heart rate data available.")

        # Calculate weight loss/gain by month
        monthly_weights = defaultdict(list)
        for date, weight in zip(dates, weights):
            year_month = (date.year, date.month)
            monthly_weights[year_month].append((date, weight))

        print("\nWeight Change by Month:")
        for year_month in sorted(monthly_weights.keys()):
            entries = monthly_weights[year_month]
            entries.sort(key=lambda x: x[0])  # Ensure entries are sorted by date
            start_weight = entries[0][1]
            end_weight = entries[-1][1]
            weight_change = end_weight - start_weight
            month_name = datetime(year_month[0], year_month[1], 1).strftime('%B %Y')
            print(f"{month_name}: {weight_change:.2f} lbs")

    def predict_weight(self):
        """
        Predict future weight for the next 30 days using linear regression.
        """
        # Machine Learning Predictions
        self.cursor.execute("SELECT Date, Weight FROM Weights WHERE Weight IS NOT NULL ORDER BY Date")
        data = self.cursor.fetchall()

        if len(data) < 2:
            print("Not enough data for predictions.")
            return

        dates = np.array([(entry.Date - data[0].Date).days for entry in data])
        weights = np.array([entry.Weight for entry in data])

        # Using numpy.polyfit to fit a linear model
        coefficients = np.polyfit(dates, weights, deg=1)
        slope, intercept = coefficients

        # Predict next 30 days
        future_dates = np.array([dates[-1] + i for i in range(1, 31)])
        predictions = slope * future_dates + intercept

        future_dates_plot = [data[0].Date + timedelta(days=int(day)) for day in future_dates]

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot([entry.Date for entry in data], weights, label='Actual Weight')
        plt.plot(future_dates_plot, predictions, label='Predicted Weight', linestyle='--')
        plt.title('Weight Prediction for Next 30 Days')
        plt.xlabel('Date')
        plt.ylabel('Weight (lbs)')
        plt.legend()
        plt.grid(True)
        plt.show()

    def restore_data(self):
        """
        Restore data from a CSV file named 'weight_data_backup.csv'.
        """
        # Restore data from a CSV file
        backup_filename = 'weight_data_backup.csv'
        if not os.path.exists(backup_filename):
            print(f"No backup file found: {backup_filename}")
            return
        df = pd.read_csv(backup_filename)
        # Clear existing data
        self.cursor.execute("DELETE FROM Weights")
        self.conn.commit()
        # Insert backup data
        for index, row in df.iterrows():
            self.cursor.execute('''
                INSERT INTO Weights (Date, Weight, Notes, WeightTrend, SleepDrtn, RestingHr)
                VALUES (?, ?, ?, ?, ?, ?);
            ''', (row['Date'], row['Weight'], row['Notes'], row['WeightTrend'], row['SleepDrtn'], row['RestingHr']))
        self.conn.commit()
        print("Data restored successfully!")

    def export_data(self):
        """
        Export data to a CSV file named 'weight_data_export.csv'.
        """
        # Export data to a CSV file
        self.cursor.execute("SELECT * FROM Weights")
        data = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame(data, columns=columns)
        export_filename = 'weight_data_export.csv'
        df.to_csv(export_filename, index=False)
        print(f"Data exported to {export_filename}")

    def import_data(self):
        """
        Import data from a CSV file named 'weight_data_import.csv'.
        """
        # Import data from a CSV file
        import_filename = 'weight_data_import.csv'
        if not os.path.exists(import_filename):
            print(f"No import file found: {import_filename}")
            return
        df = pd.read_csv(import_filename)
        # Insert imported data
        for index, row in df.iterrows():
            try:
                self.cursor.execute('''
                    INSERT INTO Weights (Date, Weight, Notes, WeightTrend, SleepDrtn, RestingHr)
                    VALUES (?, ?, ?, ?, ?, ?);
                ''', (row['Date'], row['Weight'], row['Notes'], row['WeightTrend'], row['SleepDrtn'], row['RestingHr']))
            except Exception as e:
                # Skip duplicates or errors
                continue
        self.conn.commit()
        print("Data imported successfully!")

    def exit(self):
        """
        Close the database connection and exit the application.
        """
        # Close the pyodbc cursor and connection
        self.cursor.close()
        self.conn.close()
        print("Exiting the app.")

    def display_menu(self):
        """
        Display the interactive menu and handle user choices.
        """
        while True:
            print("\n--- Weight Tracker Menu ---")
            print("1. Add weight entry")
            print("2. Visualize weight data")
            print("3. View weight log")
            print("4. Calculate statistics")
            print("5. Update weight entry")
            print("6. Predict future weight")
            print("7. Restore data")
            print("8. Export data")
            print("9. Import data")
            print("10. Exit")
            choice = input("Choose an option (1-10): ")

            if choice == '1':
                self.add_weight_entry()
            elif choice == '2':
                self.visualize_weight_data()
            elif choice == '3':
                self.view_weight_log()
            elif choice == '4':
                self.calculate_statistics()
            elif choice == '5':
                self.update_weight_entry()
            elif choice == '6':
                self.predict_weight()
            elif choice == '7':
                self.restore_data()
            elif choice == '8':
                self.export_data()
            elif choice == '9':
                self.import_data()
            elif choice == '10':
                self.exit()
                break
            else:
                print("Invalid option. Please choose a number between 1 and 10.")

def main():
    """
    Entry point of the application.
    """
    # Create an instance of WeightTracker and start the menu loop
    tracker = WeightTracker()
    tracker.display_menu()

# Ensure the main function is called when this script is executed
if __name__ == "__main__":
    main()
