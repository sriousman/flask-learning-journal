from flask import (Flask, g, render_template, flash, redirect, url_for, request)
from flask_bcrypt import check_password_hash
from flask_login import (
                        LoginManager, login_user, logout_user,
                        login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = 'auoesh.asdhhstuh.43,uoausoehuosth3ououea.auoub!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.user = current_user
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/new', methods=('GET', 'POST'))
@login_required
def new_entry(res=[]):
    form = forms.NewEntryForm()
    r_form = forms.ResourceForm()

    if r_form.validate_on_submit():
        res.append([r_form.name.data, r_form.url.data])
        flash("You added a resource!", "success")
        return render_template('new.html', form=form, res=res)

    if form.validate_on_submit():
        entry = models.Entry.create(
            title=form.title.data,
            time_spent=form.time_spent.data,
            date=form.date.data,
            learned=form.learned.data,
            user=current_user
        )
        if res:
            for r in res:
                entry.add_resource(*r)

        flash("Alright, you created an entry!", "success")
        return redirect(url_for('details', entry_id=entry.get().id))
    return render_template('new.html', form=form, r_form=rform, res=res)


@app.route('/detail/<int:entry_id>')
@login_required
def details(entry_id):
    entry = models.Entry.select().where(models.Entry.id == entry_id).get()
    return render_template('detail.html', entry=entry)


@app.route('/edit/<int:entry_id>', methods=('GET', 'POST'))
@login_required
def edit_entry(entry_id):
    try:
        entry = models.Entry.select().where(models.Entry.id == entry_id).get()
    except Entry.DoesNotExist:
        abort(404)

    form = forms.EditForm(obj=entry)
    if request.method == 'GET':
        form.title.data = entry.title
        form.time_spent.data = entry.time_spent
        form.date.data = entry.date
        form.learned.data = entry.learned
    if form.validate_on_submit():

        query = models.Entry.update(
                                    user=current_user,
                                    title=form.title.data,
                                    time_spent=form.time_spent.data,
                                    date=form.date.data,
                                    learned=form.learned.data,
                                    resources=form.resources.data,
                                    )
        query.execute()
        flash("You have edited your entry.")
        return redirect(url_for('details', entry_id=entry.get().id))
    return render_template('edit.html', entry=entry, form=form)


@app.route('/')
def index():
    entries = models.Entry.select().limit(20)
    return render_template('index.html', entries=entries)


@app.route('/profile/<username>')
@login_required
def profile(username=None):
    return render_template('profile.html')


if __name__ == '__main__':
    models.initialize()

    app.run(debug=DEBUG, host=HOST, port=PORT)
