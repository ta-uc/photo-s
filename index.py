import glob
from flask import Flask, render_template, request, send_from_directory, make_response, abort
import datetime
import os
import json
from flask_sockets import Sockets


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SEC_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
sockets = Sockets(app)
tmpDir = "/tmp/iu/"

# Initialize
import imgdata
imgdata.init_db(app)
if not os.path.isdir(tmpDir):
    os.mkdir(tmpDir)


@sockets.route("/ws-r")
def update(ws):
    while not ws.closed:
        try:
            list = imgdata.getFileList(int(ws.receive()))
            if not len(list) == 0:
                t = []
                for photo in list:
                    t.append(photo.file_name)
                msg = json.dumps(t)
                ws.send(msg)
        except:
            pass


@app.route("/")
def index():
    files = imgdata.getFileList(0)
    return render_template("index.html", files=files)


@app.route("/upload", methods=["POST"])
def receive():
    try:
        imgdata.addPhoto(request.files["imgData"])
        return "done"
    except:
        return "failed"


@app.route("/images/<path:filename>")
def image(filename):
    res = make_response()
    if os.path.isfile(os.path.join(tmpDir, filename)):
        return send_from_directory(tmpDir, filename, mimetype="image/jpg")
    else:
        if "_t" in filename:
            photo = imgdata.getFile(filename[0:-2])
            if photo is not None:
                res.data = photo.image_t
            else:
                abort(404)
        else:
            photo = imgdata.getFile(filename)
            if photo is not None:
                res.data = photo.image
            else:
                abort(404)
        res.headers["Content-Disposition"] = 'filename=' + filename
        res.headers["Content-Type"] = "image/jpg"
        return res


@app.route("/<path:iconName>")
def icon(iconName):
    if not iconName == "ws-r":
        return send_from_directory("/static", iconName)
    else:
        return ""


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
