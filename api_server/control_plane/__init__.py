from flask import Blueprint, render_template
control_plane = Blueprint('control_plane', __name__)

from api_server.control_plane import errors


@control_plane.route("/")
def main():
    return render_template("index.html")
