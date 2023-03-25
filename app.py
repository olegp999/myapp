# Import necessary packages and modules
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import yaml
from flask_bootstrap import Bootstrap
from wtforms import Form, StringField, validators, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
import os
# from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector

 
# Define the ContactForm class using FlaskForm    
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    number = StringField('Number', validators=[DataRequired()])
    submit = SubmitField('Submit')
    


# Initialize the Flask app
app = Flask(__name__)

# Enable CSRF protection for the Flask app
csrf = CSRFProtect(app)

# Initialize the Bootstrap extension for the Flask app
Bootstrap(app)

app.config['SECRET_KEY'] = 'qqq'

password=os.getenv("MYSQL_PASSWORD")

# Configure the MySQL connection settings for the Flask app   'pscale_pw_SIttdFWRPOJWAGkZsjrUzzOSRKtJBo90ctsOEIyP2KJ'
connection = mysql.connector.connect(
host='eu-central.connect.psdb.cloud',
database='contact',
user='1oikc0akh0m4t21n76zx',
password=password,
ssl_ca='/etc/ssl/cert.pem'
)


# Define a route for the root URL that handles both GET and POST requests
@app.route('/', methods = ['POST', 'GET'])
def index():
    # Create a ContactForm instance
    cform = ContactForm()

    # If the form is validated on submission, insert the data into the database and redirect to the contacts page
    if request.method == 'POST' and cform.validate_on_submit():
        try:
            with connection.cursor() as cur:
                cur.execute("INSERT INTO contacts(name, number) VALUES (%s, %s)" , (cform.name.data, cform.number.data))
                connection.commit()
                cur.close()
                return redirect(url_for('index'))
        except:
            return 'Error'
    else:
            # return render_template('index.html', form=cform)    
        # try:
            with connection.cursor() as cur:

                # Execute a SELECT query to retrieve all the data from the "contacts" table
                cur.execute("SELECT * FROM contacts")

                # Fetch all the rows returned by the query and store them in the "cont" variable
                cont = cur.fetchall()

                # Close the cursor
                cur.close()

                # Render the contacts.html template with the "contacts" data and the ContactForm instance
                return render_template('index.html', contacts=cont, form=cform)
        # except:
        #     return 'Error'   
    

# Define a route for the contact deletion functionality 
@app.route('/del')
def contact_del():
    id = request.args.get('id')
    try:
        with connection.cursor() as cur:
        # Create a cursor object and execute a DELETE query to remove the specified contact from the database
            cur.execute("DELETE FROM contacts WHERE id = %s", (id,))

            # Commit the changes to the database and close the cursor
            connection.commit()
            cur.close()

            # Redirect the user back to the contacts page
            return redirect(url_for('index'))
    except:
        return 'Error'

@app.route('/update/<int:id>/<string:name>/<string:number>', methods = ['GET', 'POST'])
def contact_update(id, name, number):
    # Create a ContactForm instance
    cform = ContactForm()

    # If the form is validated on submission, update the data into the database and redirect to the contacts page        
    if cform.validate():
    # if request.method=='POST' and cform.validate_on_submit():
           
            try:
                with connection.cursor() as cur:
                    cur.execute("UPDATE contacts SET name=%s, number=%s WHERE id = %s" , (cform.name.data, cform.number.data, id))
                    connection.commit()
                    cur.close()
                    return redirect(url_for('index'))
            except:
                return 'Error'        

    else:
        cform.name.default = name
        cform.number.default = number
        cform.process() 
        with connection.cursor() as cur:
            # cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM contacts WHERE  id=%s" , (id,))
            cont = cur.fetchall()
            cur.close()
            return render_template('update.html', form=cform, contacts=cont)

if __name__ == ('__main__'):
    app.run(debug=True)