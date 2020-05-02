from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from tag_dh import db
from tag_dh.models import Task

bp = Blueprint('task_list', __name__)

@bp.route('/login', methods=('GET','POST'))
def login():
    if session.get("validUser", False):
        return redirect(url_for('task_list.index'))

    session['validUser'] = True
    return render_template('task_list/login.html')



@bp.route('/logout', methods=('GET','POST'))
def logout():
    session.pop('validUser', None)
    return render_template('task_list/logout.html')


@bp.route('/', methods=('GET', 'POST'))
def index():
    if not session.get('validUser', False):
        return redirect(url_for('task_list.login'))

    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('Task name is required.')
        else:
            db.session.add(Task(name=name))
            db.session.commit()
        return redirect(url_for('task_list.index'))

    tasks = Task.query.all()
    return render_template('task_list/index.html', tasks=tasks)


@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    task = Task.query.get(id)
    if task != None:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('task_list.index'))
