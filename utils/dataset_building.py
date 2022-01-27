from common import *

import mysql.connector
from mysql.connector import Error


# MYSQL
# source: https://realpython.com/python-sql-libraries/

MYSQL_SERVER = "localhost"
MYSQL_USER = "mysql"
MYSQL_PASSWORD = ""
MYSQL_DB = "wikipedia"


def create_mysql_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(e)

    return connection


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
