from collections import OrderedDict
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from flask import current_app as app
from . import database as db
from .files import download_zip
from .policy import download_uniform_policy
from .dashboard import update_auto, update_science
from escalation import scheduler

bp = Blueprint('view', __name__)
@bp.route('/', methods=('GET','POST'))

def view():
    cranks=db.get_unique_cranks()
    curr_crank = cranks[0]
    models=db.get_submissions(curr_crank)

    if request.method == 'POST' and 'crank' in request.form:
        curr_crank = request.form['crank']

    if request.method == 'POST' and 'submit' in request.form and request.form['submit'] == 'Delete file':
        if request.form['adminkey'] != app.config['ADMIN_KEY']:
            flash("Incorrect admin code")
        else:
            requested=[int(x) for x in request.form.getlist('download')]
            for id in requested:
                db.remove_submission(id)
        job2 = scheduler.add_job(func=update_auto, args=[], id = 'update_auto')        

    submissions=db.get_submissions(curr_crank)

    if request.method == 'POST' and  'submit' in request.form and request.form['submit'] == 'Download files':
        
        requested=[int(x) for x in request.form.getlist('download')]
        submissions = [sub for sub in submissions if sub.id in requested]
        zipfile = download_zip(app.config['UPLOAD_FOLDER'],submissions, curr_crank)
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],zipfile),as_attachment=True)

    if request.method == 'POST' and 'policy_submit' in request.form:
        policy_crank = request.form['policy_crank']
        size         = request.form['cranksize']        
        submissions  = db.get_submissions(policy_crank)        
        requested    = [ int(x) for x in request.form.getlist('policy_download')]
        submissions  = [sub for sub in submissions if sub.id in requested]
        err = None
        try:
            size = int(size)
        except:
            err = "Passed in value '%s' for number of samples is not an integer"
        if size < 1:
            err = "Number of samples must be greater than 0"
        elif len(requested) == 0:
            err = "Must select a model to include"

        if err:
            flash(err)
        else:
            zipfile, explanation = download_uniform_policy(app.config['UPLOAD_FOLDER'],submissions,size, policy_crank)
            flash(explanation)
            app.logger.info(explanation)
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'],zipfile),as_attachment=True)
        
    elif request.method == 'POST' and 'policy_crank' in request.form:
        curr_crank = request.form['policy_crank']
        models = db.get_submissions(curr_crank)
    
    return render_template('index.html',submissions=submissions,cranks=cranks, curr_crank=curr_crank, models=models)
