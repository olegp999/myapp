from dotenv import load_dotenv
load_dotenv()
import os
import MySQLdb

connection = MySQLdb.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USERNAME"),
    passwd=os.getenv("PASSWORD"),
    db=os.getenv("DATABASE"),
    ssl={
        'ca': os.getenv("SSL_CERT")
    }
)




sql = '''CREATE TABLE contact_manager2(
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  number VARCHAR(255) NOT NULL,
  PRIMARY KEY (id)
);'''


cursor = connection.cursor()

# execute the query
cursor.execute(sql)

# fetch the data
data = cursor.fetchall()


# close the cursor and connection
cursor.close()
connection.close()