import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector

load_dotenv()

# print(os.getenv("SSL_CERT"))



connection = mysql.connector.connect(
host='eu-central.connect.psdb.cloud',
database='contact',
user='1oikc0akh0m4t21n76zx',
password=os.getenv("PASSWORD"),
ssl_ca='/etc/ssl/cert.pem'
)


sql = '''DROP TABLE contact_manager;'''


# sql = '''CREATE TABLE contact_manager(
#   id INT NOT NULL AUTO_INCREMENT,
#   name VARCHAR(255) NOT NULL,
#   number VARCHAR(255) NOT NULL,
#   PRIMARY KEY (id)
# );'''

with connection.cursor() as cur:
    cur.execute(sql)
    connection.close()

