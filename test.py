from flask import Flask
from flask_mysqldb import MySQL


app = Flask(__name__)



app.config['MYSQL_HOST'] = 'eu-central.connect.psdb.cloud' 
app.config['MYSQL_USER'] = '1oikc0akh0m4t21n76zx'
app.config['MYSQL_PASSWORD'] = 'pscale_pw_SIttdFWRPOJWAGkZsjrUzzOSRKtJBo90ctsOEIyP2KJ'
app.config['MYSQL_DB'] = 'contact'

mysql = MySQL(app)

# sql = '''CREATE TABLE contacts(
#   id INT NOT NULL AUTO_INCREMENT,
#   email VARCHAR(255) NOT NULL UNIQUE,
#   password VARCHAR(255) NOT NULL,
#   name VARCHAR(255) NOT NULL,
#   PRIMARY KEY (id)
# );'''


sql = '''CREATE TABLE contact_manager(
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  number VARCHAR(255) NOT NULL,
  PRIMARY KEY (id)
);'''

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute(sql)
    mysql.connection.commit()
    cur.close()