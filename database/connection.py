import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import tkinter as tk
from tkinter import messagebox

class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect( **DB_CONFIG )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Connected to MySQL database")
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
            self.connection = None
            self.cursor = None

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return True
        except Error as e:
            messagebox.showerror("Query Error", f"Error executing query: {e}")
            return False

    def fetch_all(self):
        return self.cursor.fetchall()

    def fetch_one(self):
        return self.cursor.fetchone()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed")
