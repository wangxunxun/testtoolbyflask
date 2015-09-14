from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User,Version
from .. import db
from ..mem_db import successDataStr

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    c_objs = {
              
            'id': user.id,
            'username': user.username,
            'email': user.email

        }
    print(111)
    return successDataStr(c_objs)



@api.route('/users/', methods=['POST'])
def new_user():
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json())


@api.route('/version', methods=['GET'])
def get_version():
    version = Version.query.first()
    c_objs = {
        "appVersion": {
            "id": version.id,
            "version": version.version_number,
            "uploadTime": str(version.update_time),
            "downloadURL": version.download_url
        }
    }
    return successDataStr(c_objs)
