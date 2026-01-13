from flask import Blueprint,render_template,redirect,url_for,flash,session,request
from app.forms import LoginForm,RegistrationForm
from app import mongo # Import the mongo instanceed in __init__.py file 
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from app.routes.chat import get_all

auth_bp = Blueprint('auth',__name__)


def insert_user(db, name, email, password):
    """Insert a new user with hashed password."""
    try:
        users_collection = db.users
        user_data = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),  # In a real application, ensure to hash the password before storing it
            'followers':[],
            'following':['68f9b3f9b2baa9fbe8ad2bd9'],
            'about':'Hi, I am use venture',
            'lastSeen': datetime.now(),
            'createdAt': datetime.now()
        }
        users_collection.insert_one(user_data)
    except Exception as e:
        print(f"Error : {e}")

def get_user_by_email(db, email):
    """Retrieve a user by email."""
    try:
        users_collection = db.users
        return users_collection.find_one({'email': email.strip().lower()})
    except Exception as e:
        print(f"Error : {e}")


def user_status_online(db,email):
    """Update user online status."""
    try:
        changeStatus = db.users
        changeStatus.update_one(
            {'email':email},
            {"$set":{"online":True}}
        )   
    except Exception as e:
        print(f"Error : {e}")
    
def user_status_offline(db,email):
    """Update user offline status."""
    try:
        changeStatus = db.users
        changeStatus.update_one(
            {'email':email},
            {"$set":{"online":False}}
        )  
    except Exception as e:
        print(f"Error : {e}")

   
@auth_bp.route("/")
def dashboard():
    """Dashboard — accessible only if logged in."""

    if 'email' not in session:
        return redirect(url_for('auth.login'))

    users = get_all(mongo.db)
    users_followed = get_user_by_email(mongo.db,session['email'])
 
    data = users if users else []

    return render_template('index.html',user_list=data,users_followed=users_followed)

@auth_bp.route("/login",methods=["GET","POST"])
def login():
    """Login route."""

    form = LoginForm()
    if form.validate_on_submit():
        # session.permanent = True
        email = form.email.data.strip().lower()
        password = form.password.data
        user = get_user_by_email(mongo.db,email)

        if user and check_password_hash(user['password'],password):
            user_status_online(mongo.db,email)
            session['name'] = user['name']
            session['about'] = user['about'] 
            session['email'] = email
            session['user_id'] = user['_id']
            # flash("Login Successful","success")
            return redirect(url_for('auth.dashboard'))  # Redirect to a dashboard or home page
        else:
            if not user:
                flash("User does not exist. Please register first.","error")
            else:
                flash("Incorrect password. Please try again.","error")
            return redirect(url_for('auth.login'))
        
    return render_template('login.html',form=form)


@auth_bp.route("/register",methods=["GET","POST"])
def register():
    """Registration route."""

    form = RegistrationForm()
    if form.validate_on_submit():
        if get_user_by_email(mongo.db,form.email.data):
            flash("This email is already in use. Please try a different email address.", "error")
            return redirect(url_for('auth.register'))
        
        name = form.name.data
        email = form.email.data.lower()
        password = form.password.data
        insert_user(mongo.db, name, email, password)

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))
        # You can add code here to save the user to the database
    return render_template('register.html',form=form)

@auth_bp.route('/logout',methods=["GET"])
def logout():
    if 'email' in session:
        email = session['email']
        user_status_offline(mongo.db,email)
        session.clear()
        flash("Logged out successfully!", "success")
    return redirect(url_for('auth.login'))