from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from tag_dh import db
from tag_dh.models import *

bp = Blueprint('clashes', __name__)

@bp.route("/clashes", methods=["GET", "POST"])
def index():
    if not session.get('validUser', False):
        return redirect(url_for('task_list.login', next="clashes.index"))
    
    if request.method == "POST":
        name = request.form['name']
        if not name:
            flash('Clash name is required.')
        else:
            clash = Clash(name=name)
            calink = ClashAccountLink(relationType="creator")
            calink.account = session["account"]
            clash.accounts.append(calink)
            db.session.add(clash)
            db.session.commit()
        return redirect(url_for('clashes.index'))
        
    return render_template('clashes/index.html')

@bp.route('/', methods=['GET'])
def mainindex():
    return redirect(url_for("task_list.index"))