from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
# import psycopg2 adapter
import psycopg2
# this module is necessary to get column names of the table
import time
from .config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
#     try:
#         # create connection to the database
#         conn = psycopg2.connect(host='localhost', database='socialmedia', user='postgres',
#         password='Septre#89654', cursor_factory=RealDictCursor)
#         # create cursor to execute sql statement
#         cursor= conn.cursor()
#         print("Database connection was successful")
#         break

#     except Exception as error:

#         print("Connection to databased failed")
#         print("Error", error)
#         time.sleep(2)
