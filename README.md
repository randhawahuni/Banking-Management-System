# Banking-Management-System
To run the provided Python script that integrates a GUI-based banking system using Tkinter and a MySQL database, you will need to follow several steps to ensure everything is correctly set up. Here is a comprehensive guide on what you need to do:

# 1. Install Python

Ensure that Python is installed on your system. Python can be downloaded from python.org. Make sure to add Python to your system's PATH during the installation.

# 2. Install Required Packages

You'll need to install several Python packages that the script relies on, including mysql-connector-python for database operations and tkinter for the GUI (Tkinter is typically included with Python). Install them using pip:

    pip install mysql-connector-python

If you find that Tkinter is not installed, you can install it via your system's package manager:

    For Ubuntu: sudo apt-get install python3-tk
    For Windows, Tkinter should be included with the Python installation.

# 3. Set Up MySQL Database

You need a running MySQL server. You can install MySQL Server from the MySQL official site or use services like XAMPP or WAMP if you are on Windows.
Creating the Database and Required Tables

Once MySQL is set up, you need to create the database and tables. Use the MySQL command line or a GUI like phpMyAdmin. Here’s an example of how you might set it up:

    CREATE DATABASE bank_db;
    USE bank_db;
    
    CREATE TABLE accounts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        account_type VARCHAR(50) NOT NULL,
        balance DECIMAL(10, 2) NOT NULL,
        session_token VARCHAR(255) UNIQUE NOT NULL
    );

    CREATE TABLE transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        transaction_type VARCHAR(50) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        date DATETIME NOT NULL
    );

# 4. Configure Python Script

Make sure to modify the database connection details in your Python script to match your MySQL configuration:

    mydb = mysql.connector.connect(
        host="localhost",  # or your host
        user="your_username",  # your MySQL username
        password="your_password",  # your MySQL password
        database="bank_db"  # the database name you created
    )

# 5. Running the Script

Open a command prompt or terminal, navigate to the directory containing your script, and run:

    python filename.py

Replace filename.py with the name of your Python script.

# 6. Using the Application

When you run the script, a GUI window should appear where you can interact with the application. Start by creating an account, logging in, and then exploring the functionalities like depositing, withdrawing, and transferring funds.
