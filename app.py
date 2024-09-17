from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:football8114@localhost:5432/project_user'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = "Secret"


connect_db(app)

ctx = app.app_context()
ctx.push()
db.create_all()


debug = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    return redirect('/register')


# This is the route an user will use to register
@app.route("/register", methods = ["GET", "POST"])
def register():

    form = RegisterForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email =  form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()

        session['username'] = user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f'/users/{user.username}')

    return render_template('register.html', form = form)


# This is the route a user will use to login
@app.route("/login", methods = ["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        exist_user = User.query.filter_by(username = username).first()

        if exist_user and exist_user.password == password:
            
            session['username'] = exist_user.username 
            flash('Welcome! Successfully Logged in!', "success")
            return redirect(f'/users/{exist_user.username}')
        else:
            # re-render the login page with an error
            form.username.errors = ["Bad name/password"]
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():

    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/login')

@app.route("/users/<username>")
def show_user(username):

    if "username" not in session or username != session['username']:
        flash("Must login in")
        return redirect('/login')
    
    user = User.query.get(username)
    form = DeleteForm()
    
    return render_template("users.html", user=user, form=form)

@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user nad redirect to login."""

    if "username" not in session:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")

@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """Show add-feedback form and process it."""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback( title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("new.html", form=form)
    

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("edit.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    return redirect(f"/users/{feedback.username}")





if __name__ == '__main__':
    app.run(debug=True)