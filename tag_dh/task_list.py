from functools import partial

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from tag_dh import db
from tag_dh.models import *

bp = Blueprint('task_list', __name__)

ROLES = ["student", "teacher", "admin"]
def stage(account):
    if account is None:
        return -1
    if account in ROLES:
        return ROLES.index(account)
    role = getattr(account, "role", None)
    if role in ROLES:
        return ROLES.index(role)
    return -1

def getaccount():
    return Account.query.filter(Account.user == session.get("username")).first()

def atleast(minimum):
    return stage(minimum) <= stage(getaccount())

render_template = partial(render_template, atleast=atleast)


@bp.route('/', methods=['GET'])
def index():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))
    return redirect(url_for('task_list.tasks'))

@bp.route('/student', methods=('GET',))
def student():
    return render_template('task_list/student.html')

@bp.route('/teacher', methods=('GET',))
def teacher():
    return render_template('task_list/teacher.html')

@bp.route('/tasks', methods=('GET', 'POST'))
def tasks():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    if request.method == 'POST':
        if not atleast("teacher"):
            flash("You don't have enough permissions to remove tasks")
            return redirect(url_for('task_list.tasks'))
        
        name = request.form['name']
        if not name:
            flash('Task name is required.')
            return redirect(url_for('task_list.tasks'))

        db.session.add(Task(name=name))
        db.session.commit()
        return redirect(url_for('task_list.tasks'))

    tasks = Task.query.all()
    return render_template('task_list/tasks.html', tasks=tasks)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        chk_password = request.form["chk_password"]
        if password != chk_password:
            flash("The passwords don't match")
            return redirect(url_for('task_list.signup'))
        
        db.session.add(Account(user=username, pwrd=password, role="student"))
        db.session.commit()
        flash("Account successfully created")
        return redirect(url_for('task_list.index'))

    return render_template('task_list/signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("account"):
        return redirect(url_for('task_list.index'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        account = (
            Account.query
            .filter(Account.user == username)
            .filter(Account.pwrd == password)
            .first()
        )
        if account is None:
            flash("Incorrect username or password")
            return redirect(url_for('task_list.login'))
        
        session['username'] = username
        return redirect(url_for('task_list.index'))

    return render_template('task_list/login.html')

@bp.route('/logout', methods=['GET','POST'])
def logout():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    session['account'] = None
    flash("You have been logged out.")
    return redirect(url_for('task_list.login'))


@bp.route('/tasks/<int:id>/delete', methods=('POST',))
def delete(id):
    if not atleast("teacher"):
        flash("You don't have enough permissions to remove tasks")
        return redirect(url_for('task_list.tasks'))
    
    task = Task.query.get(id)
    if task is not None:
        db.session.delete(task)
        db.session.commit()
    
    return redirect(url_for('task_list.tasks'))
