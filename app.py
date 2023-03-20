# Import necessary packages and modules
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import yaml
from flask_bootstrap import Bootstrap
from wtforms import Form, StringField, validators, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

 
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

# Load database configuration information from the db.yaml file
db = yaml.safe_load(open('db.yaml'))

# Configure the MySQL connection settings for the Flask app
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'contact_manager'
app.config['SECRET_KEY'] = 'qqq'

# Initialize the MySQL extension for the Flask app
mysql = MySQL(app)

# Define a route for the root URL that handles both GET and POST requests
@app.route('/', methods = ['POST', 'GET'])
def index():
    # Create a ContactForm instance
    cform = ContactForm()

    # If the form is validated on submission, insert the data into the database and redirect to the contacts page
    if request.method == 'POST' and cform.validate_on_submit():
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO contacts(name, number) VALUES (%s, %s)" , (cform.name.data, cform.number.data))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('index'))
        except:
            return 'Error'
    else:    
        try:
            with mysql.connection.cursor() as cur:

                # Execute a SELECT query to retrieve all the data from the "contacts" table
                cur.execute("SELECT * FROM contacts")

                # Fetch all the rows returned by the query and store them in the "cont" variable
                cont = cur.fetchall()

                # Close the cursor
                cur.close()

                # Render the contacts.html template with the "contacts" data and the ContactForm instance
                return render_template('index.html', contacts=cont, form=cform)
        except:
            return 'Error'   

# Define a route for the contact deletion functionality 
@app.route('/del')
def contact_del():
    id = request.args.get('id')
    try:
        with mysql.connection.cursor() as cur:
        # Create a cursor object and execute a DELETE query to remove the specified contact from the database
            cur.execute("DELETE FROM contacts WHERE id = %s", (id,))

            # Commit the changes to the database and close the cursor
            mysql.connection.commit()
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
                with mysql.connection.cursor() as cur:
                    cur.execute("UPDATE contacts SET name=%s, number=%s WHERE id = %s" , (cform.name.data, cform.number.data, id))
                    mysql.connection.commit()
                    cur.close()
                    return redirect(url_for('index'))
            except:
                return 'Error'        

    else:
        cform.name.default = name
        cform.number.default = number
        cform.process() 
        with mysql.connection.cursor() as cur:
            # cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM contacts WHERE  id=%s" , (id,))
            cont = cur.fetchall()
            cur.close()
            return render_template('update.html', form=cform, contacts=cont)

if __name__ == ('__main__'):
    app.run(debug=True)