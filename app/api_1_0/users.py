from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User
from .. import db

@api.route('/users/<int:id>')
def get_user(id):
    print(111)
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/', methods=['POST'])
def new_user():
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json())