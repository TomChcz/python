from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from amos_helpers import *

app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///../db/amos.db")

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    # if GET user, redirect to homepage
    if request.method == "GET":
        return redirect(url_for("index"))
    
    # logout any users
    session.clear()
    
    # make sure fields are completed by user
    if request.form.get("name") =="" or request.form.get("email") == "" or request.form.get("password") == "":
        return render_template("failure.html")
    
    # query database for user_email and generate error page if user_email already registered
    rows = db.execute("SELECT * FROM users WHERE user_email = :user_email", user_email=request.form.get("email"))
    if len(rows) == 1:
        return render_template("signup_result.html", user_email=request.form.get("email"))
    else:
        # insert user to database, hash the password
        db.execute("INSERT INTO users (user_name, user_email, hash) VALUES(:user_name, :user_email, :hash)", user_name=request.form.get("name"), user_email=request.form.get("email"), hash=pwd_context.hash(request.form.get("password")))
        # TODO insert email as lowercase
        
        
        # remember user and send to dashboard
        rows = db.execute("SELECT * FROM users WHERE user_email = :user_email", user_email=request.form.get("email"))
        session["user_session"] = rows[0]["user_id"]
        
        return redirect(url_for("dashboard"))
        
@app.route("/users")
@login_required
def users():
    rows = db.execute("SELECT * FROM users")
    return render_template("users.html", users=rows, logged_user=session.get("user_session"))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Sign user in"""

    # clear previous sessions
    session.clear()
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # ensure user credentials were submitted
        if not request.form.get("email"):
            return render_template("signin_error.html", error="no email provided")
        
        elif not request.form.get("password"):
            return render_template("signin_error.html", error="no password provided")
        
        # query database for user_email
        rows = db.execute("SELECT * FROM users WHERE user_email = :user_email", user_email=request.form.get("email"))
        
        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("signin_error.html", error="wrong email or password")

        # remember which user has logged in
        session["user_session"] = rows[0]["user_id"] # rows is array [0 = row zero][user_is is field in db user_id]
        
        # redirect user to dashboard
        return redirect(url_for("dashboard"))
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect(url_for("index"))

# this generates the main user dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    # query user details based on logged in session
    rows = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session.get("user_session"))
    return render_template("dashboard.html", users=rows)
    
# this app takes user input from form and generates test accordingly
@app.route("/test_generator", methods=["GET", "POST"])
def test_generator():
    # render selected test
    if request.method == "POST":
        rows = db.execute("SELECT * FROM math_exercises WHERE test_group = :test_group", test_group=request.form.get("test_group"))
        return render_template("test.html", exercises=rows)
     
    #if GET method, redirect to dashboard   
    else:
        return redirect(url_for("dashboard")) 
    

@app.route("/test_check", methods=["GET", "POST"])
def test_check():

    # answer counters
    correct = 0
    wrong = 0

    # remember test size for dynamic iteration over input fields
    input_fields = int(request.form.get("test_size"))
    
    # check input type
    inputtype = type(input_fields)
    
    # get answers and solutions and description from user input
    answers = request.form.getlist("answer")
    solutions = request.form.getlist("solution")
    descriptions = request.form.getlist("description")
    
    # devel info, to be deleted
    answers_type = type(answers)
    solutions_type = type(solutions)
    descriptions_type = type(descriptions)
    
    scores_index = []
    
    # iterate over answers and solutions
    for i in range(input_fields):
        if answers[i] == solutions[i]:
            correct += 1
            scores_index.append("Spravne")
        else:
            wrong += 1
            scores_index.append("Spatne")
            
    # TODO create dict with answers and correct or wrong
    
    # calculate success rate
    success_rate = (correct / input_fields) * 100
     
    return render_template("test_result.html", answers=answers, solutions=solutions, scores_index=scores_index, descriptions_type=descriptions_type, input_fields=input_fields, correct=correct, wrong=wrong, inputtype=inputtype, answers_type=answers_type, solutions_type=solutions_type, success_rate=success_rate, descriptions=descriptions)
    # check that all form data submitted
