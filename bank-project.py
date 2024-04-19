import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from hashlib import sha256
from secrets import token_hex

# For database operations, make sure to import mysql.connector and any specific exceptions it defines
import mysql.connector
from mysql.connector import IntegrityError

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="banking_system"
)
mycursor = mydb.cursor()

class BankingGUI:
    def __init__(self, master):
        self.master = master
        master.title("Banking System")

        # Create the login frame
        self.login_frame = ttk.Frame(master)
        self.login_frame.pack(pady=20)

        self.username_label = ttk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        self.password_label = ttk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.create_account_button = ttk.Button(self.login_frame, text="Create Account", command=self.create_account)
        self.create_account_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # Create the main application frame
        self.app_frame = ttk.Frame(master)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        session_token = authenticate_user(username, password)
        if session_token:
            self.login_frame.pack_forget()
            self.app_frame.pack(pady=20)
            self.create_widgets()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def create_account(self):
        # Call the create_account function without arguments
        session_token = create_account()

        if session_token:
            messagebox.showinfo("Account Created", "Account created successfully.")
            # Add additional functionality here if needed
        else:
            messagebox.showerror("Account Creation Failed", "Failed to create account.")

    def create_widgets(self):
        # Functionality buttons
        self.deposit_button = ttk.Button(self.app_frame, text="Deposit", command=self.deposit)
        self.deposit_button.grid(row=0, column=0, padx=10, pady=10)

        self.withdraw_button = ttk.Button(self.app_frame, text="Withdraw", command=self.withdraw)
        self.withdraw_button.grid(row=0, column=1, padx=10, pady=10)

        self.transfer_button = ttk.Button(self.app_frame, text="Transfer", command=self.transfer)
        self.transfer_button.grid(row=0, column=2, padx=10, pady=10)

        self.transactions_button = ttk.Button(self.app_frame, text="View Transactions", command=self.view_transactions)
        self.transactions_button.grid(row=1, column=0, padx=10, pady=10)

        self.balance_button = ttk.Button(self.app_frame, text="View Balance", command=self.view_balance)
        self.balance_button.grid(row=1, column=1, padx=10, pady=10)

        self.logout_button = ttk.Button(self.app_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=1, column=2, padx=10, pady=10)

    def deposit(self):
        amount = float(input("Enter the amount to deposit: "))
        session_token = input("Enter your session token: ")
        deposit_cash(session_token, amount)

    def withdraw(self):
        amount = float(input("Enter the amount to withdraw: "))
        session_token = input("Enter your session token: ")
        withdraw_cash(session_token, amount)

    def transfer(self):
        recipient_username = input("Enter recipient username: ")
        amount = float(input("Enter the amount to transfer: "))
        session_token = input("Enter your session token: ")
        transfer_funds(session_token, recipient_username, amount)

    def view_transactions(self):
        session_token = input("Enter your session token: ")
        view_transactions(session_token)

    def view_balance(self):
        session_token = input("Enter your session token: ")
        view_balance(session_token)

    def logout(self):
        self.app_frame.pack_forget()
        self.login_frame.pack(pady=20)

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

def view_transactions(session_token):
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
                    print(f"Date: {transaction[3]}, Type: {transaction[2]}, Amount: {transaction[4]}")
            else:
                print("No transactions found.")
        else:
            print("Invalid session token.")
    except Exception as e:
        print("An error occurred:", e)

def view_balance(session_token):
    try:
        # Retrieve account details
        sql = "SELECT balance FROM accounts WHERE session_token = %s"
        val = (session_token,)
        mycursor.execute(sql, val)
        balance = mycursor.fetchone()[0]

        print(f"Your current balance is: {balance}")
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

root = tk.Tk()
banking_gui = BankingGUI(root)
root.mainloop()
