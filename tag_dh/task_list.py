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

render_template = partial(
    render_template, 
    atleast=atleast,
    session=session,
    getaccount=getaccount,
)


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

@bp.route('/toggle_dark', methods=['GET'])
def toggle_dark():
    session["dark"] = not session.get("dark", False)
    return redirect(url_for(request.args.get("next", "task_list.index")))

@bp.route('/tasks', methods=('GET', 'POST'))
def tasks():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    if request.method == "GET":
        tasks = Task.query.all()
        return render_template('task_list/tasks.html', tasks=tasks)

    if not atleast("teacher"):
        flash("You don't have enough permissions to remove tasks")
        return redirect(url_for('task_list.tasks'))

    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('Task name is required.')
            return redirect(url_for('task_list.tasks'))
        
        task = Task(name=name)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('task_list.task', id=task.id))


@bp.route('/tasks/<int:id>', methods=["GET", "POST", "DELETE"])
def task(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    task = Task.query.get(id)
    account = getaccount()

    if request.method == "GET":
        submissions = task.submissions
        return render_template('task_list/task.html', id=id, task=task, submissions=submissions)
    
    if request.method == 'POST':
        text = request.form['text']
        if not text:
            flash('Submission text cannot be empty.')
            return redirect(url_for('task_list.task', id))
        
        submission = Submission(text=text, task=task, account=account)
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for('task_list.submission', id=submission.id))

    # need teacher for delete
    if not atleast("teacher"):
        flash("You don't have enough permissions to remove tasks")
        return redirect(url_for('task_list.task', id=id))
    
    if request.method == "DELETE":
        if task is not None:
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for('task_list.tasks'))


@bp.route('/submission/<int:id>', methods=["GET", "POST", "DELETE"])
def submission(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    submission = Submission.query.get(id)
    task = Task.query.get(submission.task.id)
    account = getaccount()

    if request.method == "GET":
        return render_template('task_list/submission.html', id=id, task=task, submission=submission)

    # need teacher for delete
    if not atleast("teacher"):
        flash("You don't have enough permissions to remove tasks")
        return redirect(url_for('task_list.submission', id=id))
    
    if request.method == "POST":
        mark = request.form['mark']
        try:
            mark = (int(mark) if mark else None)
        except ValueError:
            flash("Mark must be a number or empty.")
            return redirect(url_for('task_list.submission', id=id))
        
        if mark is not None and not 0 <= mark <= 100:
            flash("Mark must be from 0 to 100.")
            return redirect(url_for('task_list.submission', id=id))

        submission.percent_mark = mark
        db.session.commit()
        return redirect(url_for('task_list.submission', id=id))
    
    if request.method == "DELETE":
        if submission is not None:
            db.session.delete(submission)
            db.session.commit()
        return redirect(url_for('task_list.task', id=task.id))



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
