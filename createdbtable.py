from flask import Flask
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

db = yaml.safe_load(open('db.yaml'))

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = 'contact_manager'

mysql = MySQL(app)

# sql = '''CREATE TABLE contacts(
#   id INT NOT NULL AUTO_INCREMENT,
#   email VARCHAR(255) NOT NULL UNIQUE,
#   password VARCHAR(255) NOT NULL,
#   name VARCHAR(255) NOT NULL,
#   PRIMARY KEY (id)
# );'''


sql = '''CREATE TABLE contacts(
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  number VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  PRIMARY KEY (id)
);'''

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute(sql)
    mysql.connection.commit()
    cur.close()
