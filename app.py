from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import logging
import uuid 

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

class Trainlist(db.Model):
    train_no = db.Column(db.String(100), primary_key=True, nullable=False)
    train_name = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    runs_on = db.Column(db.String(255), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    quota = db.Column(db.String(50), nullable=False)
    reservation_coach = db.Column(db.String(50), nullable=False)
    pwd_concession = db.Column(db.Boolean, nullable=False)
    twab = db.Column(db.Boolean, nullable=False)
    general_quota_price = db.Column(db.DECIMAL(10,2))
    ac1st_quota_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    ac2nd_quota_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    ac3rd_quota_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    sleeper_quota_price = db.Column(db.DECIMAL(10,2))

class Bookingdetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    seat_preference = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    card_number = db.Column(db.String(20))
    expiry = db.Column(db.String(10))
    cvv = db.Column(db.String(10))
    name_on_card = db.Column(db.String(100))
    upi_id = db.Column(db.String(100))

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

@app.route('/book_ticket')
@login_required
def book_ticket():
    return render_template('book_ticket.html')

@app.route('/show_available_trains', methods=['GET', 'POST'])
def show_available_trains():
    if request.method == 'POST':
        from_location = request.form['from']
        to_location = request.form['to']
        journey_date = request.form['date']
        quota = request.form['quota']
        reservation_coach = request.form['coach']
        pwd_concession = 'pwd' in request.form
        twab = 'TWAB' in request.form
        
        # Query the database to check for available trains
        matching_trains = Trainlist.query.filter(
            Trainlist.from_location == from_location,
            Trainlist.to_location == to_location,
            Trainlist.journey_date == journey_date,
            Trainlist.quota == quota,
            Trainlist.reservation_coach == reservation_coach,
            Trainlist.pwd_concession == pwd_concession,
            Trainlist.twab == twab
        ).all()
        
        if matching_trains:
            # Render the trains list page with the matching trains
            return render_template('show_available_trains.html', trainlists =matching_trains)
        else:
            # Render a page indicating no trains are available
            return render_template('no_trains_available.html')
    
    # If the request method is GET, render the book ticket form
    return render_template('book_ticket.html')

# Add a new train to the database --------------------------------
# @app.route("/add_train", methods=["GET","POST"])
# @admin_required
# def add_train():
#     """Adds a new train to the database."""
#     if request.method=="POST": 
#         try:
#             newTrain = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['date'], "%d/%m/%Y %
#             newTrain = Trains(request.form["From"], request.form["To"], datetime.strptime(request.form["Date"]+ " "+ request.form["
#             # Create a new Train object and populate it with data from the POST request
#             new_train = Trains(request.form["from"], request.form["to"], datetime.strptime(request.form["when"], "%d/%m/%Y %
#             new_train = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['date'], "%d/%m/%Y %
#             new_train = Trains(request.form["From"], request.form["To"], datetime.strptime(request.form["Date"]+ " "+ request.form["
#             new_train = Trains(request.form["from"], request.form["to"], datetime.strptime(request.form["when"], "%d/%m/%Y %
#             new_train = Trains(request.form["from"], request.form["to"], datetime.strptime(request.form["when"], "%d/%m/%Y %
#             new_train = Trains(request.form["From"], request.form["To"], datetime.strptime(request.form["Date"] + " " + request.form
#             new_train = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['date'], "%d/%m/%Y %
#             new_train = Trains(request.form["from"], request.form["to"], datetime.strptime(request.form["date"]+ " "+ request.form["
#             newTrain = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['date'] + " " + request.form
#             new_train = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['dep'], "%H:%M").time(),
#             new_train = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['date'], '%d/%m/%Y %
#             new_train = Trains(request.form['from'], request.form['to'], datetime.strptime(request.form['date'], "%d/%m/%Y").


def generate_pnr():
    # Generate a UUID (Universally Unique Identifier) and return its hexadecimal representation
    return uuid.uuid4().hex[:12]

@app.route('/ticket_detail', methods=['GET', 'POST'])
def ticket_detail():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        seat_preference = request.form.get('seat_preference')
        payment_method = request.form.get('payment_method')
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        name_on_card = request.form.get('name_on_card')
        upi_id = request.form.get('upi_id')

        # Create a new TicketDetails object and add it to the database
        new_ticket = Bookingdetails(
            name=name,
            age=age,
            gender=gender,
            seat_preference=seat_preference,
            payment_method=payment_method,
            card_number=card_number,
            expiry=expiry,
            cvv=cvv,
            name_on_card=name_on_card,
            upi_id=upi_id
        )

        # Add the new ticket to the database session and commit
        db.session.add(new_ticket)
        db.session.commit()

        # Redirect to the ticket confirmation page
        return redirect(url_for('ticket_confirm'))

    # Render the booking form template
    return render_template('ticket_detail.html')

@app.route('/check_pnr')
@login_required
def check_pnr():
    return render_template('check_pnr.html')

@app.route('/train_status')
@login_required
def train_status():
    return render_template('train_status.html')

@app.route('/ticket_confirm')
def ticket_confirm():
    pnr_number = generate_pnr()
    # Fetch the ticket details from the SQL table
    ticket = Bookingdetails.query.first()  # Fetching the first ticket, you might need to adjust this based on your logic
    ticket = Trainlist.query.first()
    # Pass the ticket details to the HTML template
    return render_template('ticket_confirm.html', ticket=ticket)


if __name__ == '__main__':
    app.run(debug=True)