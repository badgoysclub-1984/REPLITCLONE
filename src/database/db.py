"""Database module"""
import sqlite3

class Database:
    def __init__(self, db_path='replitclone.db'):
        self.connection = sqlite3.connect(db_path)
    
    def close(self):
        self.connection.close()