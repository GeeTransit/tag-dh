from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from tag_dh import db
from tag_dh.models import Task

bp = Blueprint('task_list', __name__)

@bp.route('/login', methods=('GET',))
def login():
	return render_template('task_list/index.html')


@bp.route('/', methods=('GET', 'POST'))
def index():
	return redirect(url_for('task_list.login'))
'''
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('Task name is required.')
        else:
            db.session.add(Task(name=name))
            db.session.commit()

    tasks = Task.query.all()
    return render_template('task_list/index.html', tasks=tasks)
'''

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    task = Task.query.get(id)
    if task != None:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('task_list.index'))
