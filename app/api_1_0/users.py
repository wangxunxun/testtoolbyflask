from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User,Version
from .. import db
from ..mem_db import successDataStr,errorStr
import datetime

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

@api.route('/version', methods=['POST'])
def post_version():
    version_number = request.json.get("version_number")
    downloadURL = request.json.get("download_url")
    version = Version.query.all()
    print(version)
    if version:
        for v in version:
            db.session.delete(v)
            db.session.commit()
#        print(errorStr(2))
#        return errorStr(2)

    version = Version(version_number = version_number, download_url = downloadURL, create_time = datetime.datetime.now(),
                      update_time = datetime.datetime.now(),creator = "4545")

    db.session.add(version)
    db.session.commit()
    c_objs = {
        "appVersion": {
            "version": version.version_number,
            "uploadTime": str(version.update_time),
            "downloadURL": version.download_url
        }
    }
    return successDataStr(c_objs)
