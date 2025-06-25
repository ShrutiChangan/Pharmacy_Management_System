from database.connection import DatabaseConnection

class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def authenticate(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        self.db.execute_query(query, (username, password))
        return self.db.fetch_one()