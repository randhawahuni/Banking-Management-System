import tkinter as tk
from tkinter import ttk
from datetime import datetime
from hashlib import sha256
from secrets import token_hex
from exceptions import ValueError, TypeError, IntegrityError

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="bank_db"
)
mycursor = mydb.cursor()

# Account Management
def create_account():
    print("*** Create New Account ***")
    name = input("Enter your name: ")
    username = input("Enter a unique username: ")
    password = input("Enter a secure password: ")
    account_type = input("Enter account type (Personal/Business): ")
    balance = float(input("Enter initial deposit amount: "))

    try:
        # Check for special characters in name and username
        special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')']
        if any(char in name for char in special_chars) or any(char in username for char in special_chars):
            raise ValueError("Name and username should not contain special characters.")

        # Check password requirements
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
            raise ValueError("Password must be at least 8 characters long, contain at least one digit, and one uppercase letter.")

        # Hash the password
        hashed_password = sha256(password.encode()).hexdigest()

        # Generate a unique session token
        session_token = token_hex(16)

        # Insert new account
        sql = "INSERT INTO accounts (name, username, password, account_type, balance, session_token) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (name, username, hashed_password, account_type, balance, session_token)
        mycursor.execute(sql, val)
        mydb.commit()
        print("Account created successfully!")
        return session_token
    except ValueError as e:
        print("Error:", e)
    except Exception as e:
        print("An error occurred:", e)
        return None

def edit_account(session_token):
    print("*** Edit Account ***")
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            print("Current Account Details:")
            print("Name:", account[1])
            print("Username:", account[2])
            print("Account Type:", account[4])
            print("Balance:", account[5])

            print("\nWhat would you like to update?")
            print("1. Name")
            print("2. Password")
            print("3. Account Type")
            choice = input("Enter your choice (1/2/3): ")

            if choice == '1':
                new_name = input("Enter new name: ")
                sql = "UPDATE accounts SET name = %s WHERE session_token = %s"
                val = (new_name, session_token)
                mycursor.execute(sql, val)
                mydb.commit()
                print("Name updated successfully.")
            elif choice == '2':
                new_password = input("Enter new password: ")
                hashed_password = sha256(new_password.encode()).hexdigest()
                sql = "UPDATE accounts SET password = %s WHERE session_token = %s"
                val = (hashed_password, session_token)
                mycursor.execute(sql, val)
                mydb.commit()
                print("Password updated successfully.")
            elif choice == '3':
                new_account_type = input("Enter new account type (Personal/Business): ")
                sql = "UPDATE accounts SET account_type = %s WHERE session_token = %s"
                val = (new_account_type, session_token)
                mycursor.execute(sql, val)
                mydb.commit()
                print("Account type updated successfully.")
            else:
                print("Invalid choice.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

def close_account(session_token):
    print("*** Close Account ***")
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            # Delete the account
            sql = "DELETE FROM accounts WHERE session_token = %s"
            val = (session_token,)
            mycursor.execute(sql, val)
            mydb.commit()
            print("Account closed successfully.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

# Financial Transactions
def deposit_cash(session_token, amount):
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            # Update the account balance
            new_balance = account[5] + amount
            sql = "UPDATE accounts SET balance = %s WHERE session_token = %s"
            val = (new_balance, session_token)
            mycursor.execute(sql, val)
            mydb.commit()

            # Insert the transaction
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO transactions (username, transaction_type, amount, date) VALUES (%s, 'Deposit', %s, %s)"
            val = (account[2], amount, date)
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"Deposited {amount} into your account. New balance: {new_balance}")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

def withdraw_cash(session_token, amount):
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            # Check if the account has sufficient balance
            if account[5] >= amount:
                # Update the account balance
                new_balance = account[5] - amount
                sql = "UPDATE accounts SET balance = %s WHERE session_token = %s"
                val = (new_balance, session_token)
                mycursor.execute(sql, val)
                mydb.commit()

                # Insert the transaction
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "INSERT INTO transactions (username, transaction_type, amount, date) VALUES (%s, 'Withdrawal', %s, %s)"
                val = (account[2], amount, date)
                mycursor.execute(sql, val)
                mydb.commit()
                print(f"Withdrew {amount} from your account. New balance: {new_balance}")
            else:
                print("Insufficient balance.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

def transfer_funds(session_token, recipient_username, amount):
    try:
        # Retrieve sender's account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        sender_account = mycursor.fetchone()

        if sender_account:
            # Retrieve recipient's account details
            sql = "SELECT * FROM accounts WHERE username = %s"
            val = (recipient_username,)
            mycursor.execute(sql, val)
            recipient_account = mycursor.fetchone()

            if recipient_account:
                # Check if the sender has sufficient balance
                if sender_account[5] >= amount:
                    # Update the sender's balance
                    sender_new_balance = sender_account[5] - amount
                    sql = "UPDATE accounts SET balance = %s WHERE session_token = %s"
                    val = (sender_new_balance, session_token)
                    mycursor.execute(sql, val)

                    # Update the recipient's balance
                    recipient_new_balance = recipient_account[5] + amount
                    sql = "UPDATE accounts SET balance = %s WHERE username = %s"
                    val = (recipient_new_balance, recipient_username)
                    mycursor.execute(sql, val)
                    mydb.commit()

                    # Insert the transaction
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sql = "INSERT INTO transactions (username, transaction_type, amount, date) VALUES (%s, 'Transfer', %s, %s)"
                    val = (sender_account[2], amount, date)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    print(f"Transferred {amount} from your account to {recipient_username}. New balance: {sender_new_balance}")
                else:
                    print("Insufficient balance.")
            else:
                print("Invalid recipient username.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

def view_transactions(session_token, start_date=None, end_date=None, transaction_type=None):
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            # Retrieve transaction history
            sql = "SELECT * FROM transactions WHERE username = %s"
            val = (account[2],)
            mycursor.execute(sql, val)
            transactions = mycursor.fetchall()

            if transactions:
                print("Transaction History:")
                for transaction in transactions:
                    if start_date and transaction[3] < start_date:
                        continue
                    if end_date and transaction[3] > end_date:
                        continue
                    if transaction_type and transaction[2] != transaction_type:
                        continue
                    print(f"Date: {transaction[3]}, Type: {transaction[2]}, Amount: {transaction[4]}")
            else:
                print("No transactions found.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

# Account Services
def view_account_details(session_token):
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            print("Account Details:")
            print("Name:", account[1])
            print("Username:", account[2])
            print("Account Type:", account[4])
            print("Balance:", account[5])
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

def request_service(session_token):
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            print("Available Services:")
            print("1. Checkbook")
            print("2. Debit/Credit Card")
            print("3. Recurring Payments")
            print("4. Direct Debits")
            choice = input("Enter your choice (1/2/3/4): ")

            if choice == '1':
                # Process checkbook request
                print("Checkbook request submitted.")
            elif choice == '2':
                # Process debit/credit card request
                print("Debit/Credit card request submitted.")
            elif choice == '3':
                # Process recurring payments request
                print("Recurring payments request submitted.")
            elif choice == '4':
                # Process direct debits request
                print("Direct debits request submitted.")
            else:
                print("Invalid choice.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

# Security and Compliance
def authenticate_user(username, password):
    try:
        # Retrieve account details
        sql = "SELECT * FROM accounts WHERE username = %s"
        val = (username,)
        mycursor.execute(sql, val)
        account = mycursor.fetchone()

        if account:
            # Verify the password
            hashed_password = sha256(password.encode()).hexdigest()
            if hashed_password == account[3]:
                # Implement two-factor authentication
                # (e.g., send OTP to registered mobile number)
                print("Login successful.")
                return account[6]
            else:
                print("Invalid username or password.")
                return None
        else:
            print("Invalid username or password.")
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

class BankingGUI:
    def __init__(self, master):
        self.master = master
        master.title("Banking System")

        # Create the login frame
        self.login_frame = tk.Frame(master)
        self.login_frame.pack(pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)

        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Create the main application frame
        self.app_frame = tk.Frame(master)

        # Add your banking system functionality here
        # Example: Create an account
        self.create_account_button = tk.Button(self.app_frame, text="Create Account", command=self.create_account)
        self.create_account_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        session_token = authenticate_user(username, password)
        if session_token:
            self.login_frame.pack_forget()
            self.app_frame.pack(pady=20)
        else:
            print("Login failed.")

    def create_account(self):
        session_token = create_account()
        if session_token:
            print("Account created successfully.")
            # Add more functionality here
        else:
            print("Account creation failed.")

root = tk.Tk()
banking_gui = BankingGUI(root)
root.mainloop()
