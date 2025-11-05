"""MongoDB connection management"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Database:
    """MongoDB database connection singleton"""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Establish connection to MongoDB"""
        if self._client is None:
            try:
                mongodb_uri = os.getenv('MONGODB_URI')
                if not mongodb_uri:
                    raise ValueError("MONGODB_URI not found in environment variables")

                self._client = MongoClient(mongodb_uri)
                # Test connection
                self._client.admin.command('ping')

                db_name = os.getenv('DATABASE_NAME', 'instagram_organizer')
                self._db = self._client[db_name]

                print(f"Successfully connected to MongoDB database: {db_name}")
                return True

            except ConnectionFailure as e:
                print(f"Failed to connect to MongoDB: {e}")
                return False
            except Exception as e:
                print(f"Error connecting to database: {e}")
                return False
        return True

    def get_database(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db

    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("Database connection closed")


# Global database instance
db = Database()
