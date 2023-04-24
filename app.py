# Import necessary packages and modules
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_mysqldb import MySQL
import yaml
from flask_bootstrap import Bootstrap
from wtforms import Form, StringField, validators, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
import os
# from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

# function that sorts a list of words alphabetically and then creates alphabetical sections similar to a phone book
def index_con(con):
        # sort the contacts alphabetically by name
        con.sort(key=lambda x: x[1])
        # create a dictionary to store the alphabet sections
        alphabet_sections = {}
        for contact in con:
            # get the first letter of the name
            first_letter = contact[1][0].upper()
        
            # if the first letter is not already a key in the dictionary, add it
            if first_letter not in alphabet_sections:
                alphabet_sections[first_letter] = []
                # add the contact to the appropriate alphabet section
            alphabet_sections[first_letter].append(contact)
        return alphabet_sections.items()
 
# Define the ContactForm class using FlaskForm    
class ContactForm(FlaskForm):
    name = StringField('Enter a name', validators=[DataRequired()])
    number = StringField('Enter a phone number', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# Define the RegisterForm class using FlaskForm    
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Initialize the Flask app
app = Flask(__name__)

class User(UserMixin):
    def __init__(self, id, email, password, username):
        # initialize the object's properties
        self.id = id
        self.email = email
        self.password = password
        self.name = username

  
    @staticmethod
    def get(id):
        # create a cursor object and execute a SQL query to retrieve the user's information from the database
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
        data = cursor.fetchone()
        # if there is no data, return None
        if not data:
            return None
        # return a User object with the retrieved information
        return User(data[0], data[1], data[2], data[3])
    
# create a LoginManager instance and initialize it with the Flask app    
login_manager = LoginManager()
login_manager.init_app(app)

# configure the login manager to use the load_user function to retrieve a user's information when they log in
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

 
# connection = mysql.connector.connect(
# host='localhost',
# database='contactdb',
# user='root',
# password='Olegsql666!',
# ssl_ca='/etc/ssl/cert.pem'
# )

# Configure the MySQL connection settings for the Flask app  
connection = mysql.connector.connect(
user='sql8612757', 
password='1Tz7GuCvTz', 
host='sql8.freemysqlhosting.net', 
database='sql8612757',
ssl_ca='/etc/ssl/cert.pem'
)

@app.route('/')
def front():
        return render_template('front.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    # Create an instance of the RegisterForm class
    rform = RegisterForm()
    
    # If the request method is POST, process the form data                        if rform.validate_on_submit():  
    if request.method == 'POST':
        # Generate a hash of the password using the pbkdf2 algorithm with sha256 hash and salt length of 8
        password_hash=generate_password_hash(rform.password.data, method='pbkdf2:sha256:10000', salt_length=8,)
        
        # Try to insert the user data into the 'users' table in the database
        try:
            with connection.cursor() as cur:
                cur.execute("INSERT INTO users(email, password, name) VALUES (%s, %s, %s)", (rform.email.data, password_hash, rform.name.data))
                connection.commit()
                
                # Retrieve the user data from the database using their email
                cur.execute("SELECT * FROM users WHERE email=%s", (rform.email.data,))
                data = cur.fetchone()
                cur.close()
                
                # Create an instance of the User class with the retrieved user data and log the user in
                user = User(data[0], data[1], data[2], data[3])
                login_user(user)
                
                # Redirect the user to the 'index' page with their user id as a parameter
                return redirect(url_for('index', id=data[0]))
        except:
            # If there was an error with inserting the user data, return an error message
            return 'Error'
    
    # If the request method is GET, render the 'register.html' template with the RegisterForm instance as a parameter
    return render_template("register.html", form=rform)


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Create an instance of RegisterForm class for the login form
    rform = RegisterForm()

    # Check if the request method is POST
    if request.method == 'POST':
        try:
            # Establish a connection to the database and execute a SELECT query
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email=%s" , (rform.email.data,))
                data = cur.fetchone()
                cur.close()
                
                # Verify the password hash and create a User instance
                if check_password_hash(data[2], rform.password.data):
                    user = User(data[0], data[1], data[2], data[3])
                    # Log in the user using Flask-Login
                    login_user(user)
                    # Redirect to the index page with user ID as parameter
                    return redirect(url_for('index', id=data[0]))
                else:
                    # Flash a message for invalid credentials and redirect to login page
                    flash('Invalid email or password')
                    return redirect(url_for('login'))
                
        except:
            # If any exception is raised, return an error message
            return 'Error'    

    # Render the login.html template with the RegisterForm instance as form parameter
    return render_template('login.html', form=rform)

@app.route('/logout')
def logout():
    # Log out the user using Flask-Login and redirect to the register page
    logout_user()
    return redirect(url_for('register'))


@app.route('/projects')
def projects():
    # Render the projects.html template
    return render_template('projects.html')


@app.route('/contact')
def contact():
    # Render the contact.html template
    return render_template('contact.html')






# Define a route for the root URL that handles both GET and POST requests   
@app.route('/contacts', methods = ['POST', 'GET'])
@login_required
def index():
    # Create a ContactForm instance
    cform = ContactForm()

    # Retrieve the user ID from the query string of the URL
    id = request.args.get('id')
    
    # If the form is submitted using HTTP POST method, try to insert the form data into the 'contacts' table
    if request.method == 'POST':
        try:
            with connection.cursor() as cur:
                # Execute SQL query to insert data into the 'contacts' table
                cur.execute("INSERT INTO contacts(name, number, user_id) VALUES (%s, %s, %s)" , (cform.name.data, cform.number.data, id))
                # Commit the changes to the database
                connection.commit()
                # Close the cursor
                cur.close()
                # Redirect to the index page with the user ID
                return redirect(url_for('index', id=id))
        except:
            # Return an error message if there was an error executing the SQL query
            return 'Error'
    else:
        try:
            with connection.cursor() as cur:

                # Execute a SELECT query to retrieve all the data from the "contacts" table
                cur.execute("SELECT * FROM contacts WHERE user_id=%s", (id,))

                # Fetch all the rows returned by the query and store them in the "cont" variable
                cont = cur.fetchall()

                # Close the cursor
                cur.close()

                alphabet = index_con(cont)


                # Render the contacts.html template with the "contacts" data and the ContactForm instance
                return render_template('index.html', contacts_l=alphabet, form=cform, u_id=id)
        except:
                return 'Error'    
        





  
        

# Define a route for the contact deletion functionality 
@app.route('/del')
def contact_del():    
    id = request.args.get('id')
    user_id = request.args.get('user_id')
    try:
        with connection.cursor() as cur:
        # Create a cursor object and execute a DELETE query to remove the specified contact from the database
            cur.execute("DELETE FROM contacts WHERE id = %s", (id,))

            # Commit the changes to the database and close the cursor
            connection.commit()
            cur.close()

            # Redirect the user back to the contacts page
            return redirect(url_for('index', id=user_id))
    except:
        return 'Error'

@app.route('/update/<int:id>/<string:name>/<string:number>/<int:user_id>', methods = ['GET', 'POST'])
def contact_update(id, name, number, user_id):
    # Create a ContactForm instance
    cform = ContactForm()

    # If the form is submitted using HTTP POST method, update the data into the database and redirect to the contacts page
    if request.method=='POST':
           
            try:
                with connection.cursor() as cur:
                    cur.execute("UPDATE contacts SET name=%s, number=%s WHERE id = %s" , (cform.name.data, cform.number.data, id))
                    connection.commit()
                    cur.close()
                    return redirect(url_for('index', id=user_id))
            except:
                return 'Error'        
     # If the form is not validated on submission, pre-populate the form fields with existing data from the database
    else:
        cform.name.default = name
        cform.number.default = number
        cform.process() 
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM contacts WHERE  id=%s" , (id,))
                cont = cur.fetchone()
                cur.close()
                return render_template('update.html', form=cform, contact=cont)
        except:
            return 'Error' 
        
if __name__ == ('__main__'):
    app.run(debug=True)