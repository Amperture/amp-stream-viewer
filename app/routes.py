#{{{ Python and Flask Imports
from app import app, lm, google_bp, db
from flask import redirect, url_for, jsonify, request, send_file

from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized

from flask_login import login_required, login_user, logout_user, current_user

from app.models import User

from sqlalchemy.orm.exc import NoResultFound

import pprint
import os
#}}}
#{{{ Main Index Route. Render Webpage
@app.route('/', defaults={'path':''})
@app.route('/index', defaults={'path':''})
@app.route('/<path:path>')
def index():
    dist_dir = app.config['DIST_DIR']
    index_path = os.path.join(dist_dir, 'index.html')
    return send_file(index_path)

#}}} 
#{{{ Grabbing Profile info
@app.route('/api/userinfo')
def profileinfo():
    print(current_user) 
    if not current_user.is_authenticated:
        return jsonify({"loggedIn" : False})
    return jsonify({'name':current_user.name})
    acct = google.get('/plus/v1/people/me')
    assert acct.ok, acct.text
    return jsonify(acct.json())

#}}} 
#{{{ Stream List JSON
@app.route('/api/ytlivesearch', methods=["POST"])
def ytstreamlist():
    if google.authorized:
        print("yes")
    else: 
        print('no')
    form = request.form
    response = {}

    resp = google.get(
            '/youtube/v3/search?part=snippet&type=video&eventType=live&'
            'q=' + form['ytsearchterm'])

    print(resp.json())
    if resp.ok:
        lol = resp.json()
        return jsonify(lol)

#}}} 
#{{{ Google Login Reaction. Login User
@oauth_authorized.connect_via(google_bp)
def google_new_login(bp, token):
    acct = bp.session.get('/plus/v1/people/me')
    if acct.ok: 
        acct_json = acct.json()
        pprint.pprint(acct_json)

        email = acct_json['emails'][0]['value']
        try:
            nickname = acct_json['nickname']
            avatar = acct_json['image']['url']
        except KeyError:
            nickname = email

        query = User.query.filter_by(email=email)

        try:
            user = query.one()
            user.name = nickname
            user.avatar = avatar
            db.session.commit()
        except NoResultFound:
            user = User(name=nickname, email=email, avatar=avatar)
            db.session.add(user)
            db.session.commit()

        login_user(user)
#}}}
#{{{ Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#}}}
#{{{ User Loader
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#}}}
