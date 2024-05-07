# This is flask app done by Mirjalol , Javohir , Xalililloh , MuhammadAmin for presentation for database
# first of all we install and import the framework and libraries we need :
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy  # toolkit that define db models , interact with db and do migrations
from werkzeug.security import generate_password_hash, check_password_hash  # securing password before adding to db
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///User.db" # path to the SQLite database
app.config['SECRET_KEY'] = 'secret' # secret key for session and data protection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # by what we turn off SQLAlchemy modification tracking
db = SQLAlchemy(app) #by that we initialize SQLAlchemy to work with our db
migrate = Migrate(app, db) # initialize the db migration 


# defining an SQLAlchemy model for our "users" table
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # we have id , username , email and hashed password in our db
    username = db.Column(db.String(100), unique=True, nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False) #users hashed password

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)  # hash password during initialization


@app.route('/', methods=['GET', 'POST']) # this is route for the main page , that is login for us 
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password are required.') # flash error
            return render_template('index1.html')

        user = users.query.filter_by(username=username).first() # this line search for the user in the database
        if user: #if found , then checks for password hash
            if check_password_hash(user.password_hash, password): 
                session['username'] = username # adds username to session 
                flash('Logged in successfully!') # this actually should flash , but can't be seen , cause we instantly go to the 2 webpage
                return redirect(url_for('index1')) #this is where we redirect to the 2page
            else:
                error = 'Invalid username or password. Please try again.'
                return render_template('index1.html', error=error)
        else:
            error = 'User not found. Please register.'
            return render_template('index1.html', error=error)
    return render_template('index1.html')

# this page is used see the data in db
@app.route('/view')
def view():
    return render_template('view.html', users=users.query.all())

# register page , where we register and add a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.permanent = True
        username = request.form['username']
        session['username'] = username
        email = request.form.get('email', '')
        password = request.form['password']

        if not username or not password:
            error = 'Username and password are required.'
            return render_template('register.html', error=error)

        found_user = users.query.filter_by(username=username).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(username=username, email=email, password=password) 
            db.session.add(usr)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

# route to display the store page

@app.route('/storepage')
def index1():
    return render_template('index.html')

# common pattern in flask to run the app 
if __name__ == '__main__':
    with app.app_context():
        db.create_all() #this line creates all the database tables defined by the SQLAlchemy models
    app.run(debug=True) #it will restart automatically if the change is applied in the code
