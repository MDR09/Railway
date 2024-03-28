from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__, template_folder='template')
app.secret_key = 'railwaysprojects'

# Configuring SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/railways'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress warning

db = SQLAlchemy(app)

# Login Manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))
    role = db.Column(db.String(10), default='user')


class Showtrain(db.Model):
    ticket_id = db.Column(db.Integer, primary_key=True)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    quota = db.Column(db.String(50), nullable=False)
    reservation_coach = db.Column(db.String(50), nullable=False)
    pwd_concession = db.Column(db.Boolean, nullable=False)
    twab = db.Column(db.Boolean, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect to book ticket page if user is logged in
        return redirect(url_for('book_ticket'))
    return render_template('index.html')

@app.route('/users')
@login_required
def show_users():
    if current_user.role != 'admin':
        return "Access Denied. Only admins can view user information."
    
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/show_trains')
def show_trains():
    # Retrieve all train tickets from the database
    showtrains = Showtrain.query.all()
    return render_template('show_trains.html', showtrains=showtrains)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')  # Ensure correct field name
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email Already Exist", "warning")
            return render_template('signup.html')

        new_user = User(name=name, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Successful! Please Login", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('book_ticket'))
        else:
            flash("Invalid credentials", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/contact') 
def contact():
    return render_template('contact.html')

@app.route('/about') 
def about():
    return render_template('about.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    if request.method == 'POST':
        # Extract form data
        from_location = request.form['from']
        to_location = request.form['to']
        date = request.form['date']
        quota = request.form['quota']
        coach = request.form['coach']
        pwd_concession = True if 'pwd' in request.form else False
        twab_concession = True if 'TWAB' in request.form else False

        # Create a new train instance
        new_train = Showtrain (from_location=from_location, to_location=to_location, date=date, 
                          quota=quota, coach=coach, pwd_concession=pwd_concession, twab_concession=twab_concession)
        
        # Add to the database
        db.session.add(new_train)
        db.session.commit()
        return redirect(url_for('train_list'))
    return render_template('book_ticket.html')

@app.route('/ticket_detail')
@login_required
def ticket_detail():
    return render_template('ticket_detail.html')

@app.route('/check_pnr')
@login_required
def check_pnr():
    return render_template('check_pnr.html')

@app.route('/train_status')
@login_required
def train_status():
    return render_template('train_status.html')


if __name__ == '__main__':
    app.run(debug=True)