# Import necessary packages and modules
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
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
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

 
# Define the ContactForm class using FlaskForm    
class ContactForm(FlaskForm):
    name = StringField('Enter a name', validators=[DataRequired()])
    number = StringField('Enter a phone number', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Initialize the Flask app
app = Flask(__name__)

class User(UserMixin):
    def __init__(self, id, email, password, username):
        self.id = id
        self.email = email
        self.password = password
        self.name = username

  
    @staticmethod
    def get(id):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
        data = cursor.fetchone()
        if not data:
            return None
        return User(data[0], data[1], data[2], data[3])
    
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)    
    
# Enable CSRF protection for the Flask app
csrf = CSRFProtect(app)

# Initialize the Bootstrap extension for the Flask app
Bootstrap(app)

app.config['SECRET_KEY'] = 'qqq'

# password saved in Environment Variables on render.com
password=os.getenv("MYSQL_PASSWORD")

# Configure the MySQL connection settings for the Flask app   'pscale_pw_SIttdFWRPOJWAGkZsjrUzzOSRKtJBo90ctsOEIyP2KJ'
connection = mysql.connector.connect(
host='aws.connect.psdb.cloud',
database='contact',
user='soj9hamqpih54xafzkwt',
password=password,
ssl_ca='/etc/ssl/cert.pem'
)

@app.route('/')
def front():
    return render_template('front.html')



@app.route('/register', methods=['POST', 'GET'])
def register():
    rform = RegisterForm()
    if request.method == 'POST':
        password_hash=generate_password_hash(rform.password.data, method='pbkdf2:sha256:10000', salt_length=8,)
        try:
            with connection.cursor() as cur:
                cur.execute("INSERT INTO users(email, password, name) VALUES (%s, %s, %s)", (rform.email.data, password_hash, rform.name.data))
                connection.commit()
                cur.execute("SELECT * FROM users WHERE email=%s", (rform.email.data,))
                data = cur.fetchone()
                cur.close()
                user = User(data[0], data[1], data[2], data[3])
                login_user(user)
                return redirect(url_for('index'))
        except:
            return 'Error'
    
    return render_template("register.html", form=rform)    

@app.route('/login', methods=['POST', 'GET'])
def login():
    rform = RegisterForm()
    if request.method == 'POST':
        try:
          with connection.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email=%s" , (rform.email.data,))
                data = cur.fetchone()
                cur.close()
                if check_password_hash(data[2], rform.password.data):
                    user = User(data[0], data[1], data[2], data[3])
                    login_user(user)
                    return redirect(url_for('index', name=data[3]))
                else:
                    flash('Invalid email or password')
                    return redirect(url_for('login'))
                
        except:
                return 'Error'    
    return render_template('login.html', form=rform)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('front'))

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact')
def contact():
    logout_user()
    return render_template('contact.html')

# Define a route for the root URL that handles both GET and POST requests   
@app.route('/contacts', methods = ['POST', 'GET'])
@login_required
def index():
    # Create a ContactForm instance
    cform = ContactForm()

    name = request.args.get('name')

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
        try:
            with connection.cursor() as cur:

                # Execute a SELECT query to retrieve all the data from the "contacts" table
                cur.execute("SELECT * FROM contacts")

                # Fetch all the rows returned by the query and store them in the "cont" variable
                cont = cur.fetchall()

                # Close the cursor
                cur.close()

                # Render the contacts.html template with the "contacts" data and the ContactForm instance
                return render_template('index.html', contacts=cont, form=cform, name=name)
        except:
            return 'Error'   
    

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
            cur.execute("SELECT * FROM contacts WHERE  id=%s" , (id,))
            cont = cur.fetchone()
            cur.close()
            return render_template('update.html', form=cform, contact=cont)

if __name__ == ('__main__'):
    app.run(debug=True)