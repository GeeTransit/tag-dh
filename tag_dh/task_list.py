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

old_render_template = render_template
render_template = partial(
    old_render_template, 
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


@bp.route('/tasks/<int:id>', methods=["GET", "POST"])
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

@bp.route('/tasks/<int:id>/delete', methods=["POST"])
def taskdelete(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    task = Task.query.get(id)
    account = getaccount()
    
    if not atleast("teacher"):
        flash("You don't have enough permissions to remove tasks")
        return redirect(url_for('task_list.task', id=id))
    
    if request.method == "POST":
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
    account = Account.query.get(submission.account.id)

    if request.method == "GET":
        return render_template('task_list/submission.html', id=id, task=task, account=account, submission=submission)

    if not atleast("teacher"):
        flash("You don't have enough permissions to modify tasks")
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

@bp.route('/submission/<int:id>/delete', methods=["POST"])
def submissiondelete(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    submission = Submission.query.get(id)
    task = Task.query.get(submission.task.id)
    account = Account.query.get(submission.account.id)
    
    if not atleast("teacher"):
        flash("You don't have enough permissions to modify tasks")
        return redirect(url_for('task_list.submission', id=id))
    
    if request.method == "POST":
        if submission is not None:
            db.session.delete(submission)
            db.session.commit()
        return redirect(url_for('task_list.task', id=task.id))

@bp.route('/teams', methods=['GET', 'POST'])
def teams():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    if request.method == "GET":
        teams = Team.query.all()
        return render_template('task_list/teams.html', teams=teams)

    if not atleast("teacher"):
        flash("You don't have enough permissions to modify teams")
        return redirect(url_for('task_list.teams'))

    if request.method == 'POST':
        name = request.form['name']
        health = request.form['health']
        usernames = request.form['usernames']
        
        members = [Account.query.filter(Account.user == username).first() for username in usernames.split()]
        if not all(members):
            flash('All usernames must be real usernames.')
            return redirect(url_for('task_list.teams'))
        
        team = Team(name=name, health=health, members=members)
        db.session.add(team)
        db.session.commit()
        return redirect(url_for('task_list.team', id=team.id))

@bp.route('/teams/<int:id>', methods=["GET", "POST"])
def team(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    team = Team.query.get(id)
    account = getaccount()

    if request.method == "GET":
        members = team.members
        return render_template('task_list/team.html', id=id, team=team, members=members)

    if not atleast("teacher"):
        flash("You don't have enough permissions to modify teams")
        return redirect(url_for('task_list.team', id=id))
    
    if request.method == 'POST':
        health = request.form['health']
        try:
            health = int(health)
        except ValueError:
            flash("Mark must be a number.")
            return redirect(url_for('task_list.team', id=id))
        
        if not 0 <= health:
            flash("Health must be at least 0.")
            return redirect(url_for('task_list.team', id=id))
        
        team.health = health
        db.session.commit()
        return redirect(url_for('task_list.team', id=id))

@bp.route('/teams/<int:id>/delete', methods=["POST"])
def teamdelete(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    team = Team.query.get(id)
    account = getaccount()

    if not atleast("teacher"):
        flash("You don't have enough permissions to modify teams")
        return redirect(url_for('task_list.team', id=id))
    
    if request.method == "POST":
        if team is not None:
            db.session.delete(team)
            db.session.commit()
        return redirect(url_for('task_list.teams'))

@bp.route('/teams/create', methods=["GET"])
def create():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    if not atleast("teacher"):
        flash("You don't have enough permissions to modify teams")
        return redirect(url_for('task_list.teams'))

    if request.method == "GET":
        return render_template('task_list/create.html')

@bp.route('/profiles', methods=['GET'])
def profiles():
    if not atleast("student"):
        return redirect(url_for('task_list.login'))

    if request.method == "GET":
        accounts = Account.query.all()
        return render_template('task_list/profiles.html', accounts=accounts)

@bp.route('/profile/<int:id>', methods=["GET", "DELETE"])
def profile(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))
    
    account = Account.query.get(id)

    if request.method == "GET":
        badges = account.badges.split() if account.badges is not None else []
        submissions = account.submissions
        if not atleast("teacher"):
            if account.id != getaccount().id:
                submissions = []
        return render_template('task_list/profile.html', id=id, account=account, submissions=submissions, badges=badges)

@bp.route('/profile/<int:id>/badge', methods=["POST"])
def profilebadge(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))
    
    account = Account.query.get(id)
    
    if not atleast("teacher"):
        flash("You don't have enough permissions to modify badges")
        return redirect(url_for('task_list.profile', id=id))
    
    if request.method == "POST":
        badges = request.form['badges']
        account.badges = badges
        db.session.commit()
        return redirect(url_for('task_list.profile', id=id))

@bp.route('/profile/<int:id>/role', methods=["POST"])
def profilerole(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))
    
    account = Account.query.get(id)
    
    if not atleast("admin"):
        flash("You don't have enough permissions to modify roles")
        return redirect(url_for('task_list.profile', id=id))
    
    if request.method == "POST":
        role = request.form['role']
        if role not in ROLES:
            flash(f"Invalid role {role}: must be one of {', '.join(ROLES)}")
            return redirect(url_for('task_list.profile', id=id))
        
        account.role = role
        db.session.commit()
        return redirect(url_for('task_list.profile', id=id))

@bp.route('/profile/<int:id>/delete', methods=["POST"])
def profiledelete(id):
    if not atleast("student"):
        return redirect(url_for('task_list.login'))
    
    account = Account.query.get(id)

    if not atleast("admin"):
        flash("You don't have enough permissions to modify accounts")
        return redirect(url_for('task_list.profile', id=id))
    
    if request.method == "POST":
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('task_list.profiles'))



@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get("account"):
        return redirect(url_for('task_list.index'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        chk_password = request.form["chk_password"]
        if password != chk_password:
            flash("The passwords don't match")
            return redirect(url_for('task_list.signup'))
        
        account = Account.query.filter(Account.user == username).first()
        if account is not None:
            flash("There is a user with that username already")
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

    session['username'] = None
    flash("You have been logged out.")
    return redirect(url_for('task_list.login'))
