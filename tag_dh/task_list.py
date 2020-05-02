from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from tag_dh import db
from tag_dh.models import Task

bp = Blueprint('task_list', __name__)

@bp.route('/login', methods=('GET','POST'))
def login():
	session['validUser'] = true
	return render_template('task_list/loginpage.html')
		

@bp.route('/', methods=('GET', 'POST'))
def index():
	
	if 'username' in session:

		if request.method == 'POST':
			name = request.form['name']
			if not name:
				flash('Task name is required.')
			else:
				db.session.add(Task(name=name))
				db.session.commit()
	
		tasks = Task.query.all()
		return render_template('task_list/index.html', tasks=tasks)

	else:
		return redirect(url_for('task_list.login'))


@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    task = Task.query.get(id)
    if task != None:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('task_list.index'))
