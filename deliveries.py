from flask import Blueprint, jsonify
from flask_login import login_required

deliveries_api = Blueprint("deliveries_api", __name__)


@deliveries_api.route("/")
@login_required
def list_deliveries():
    return jsonify({"ok": True, "deliveries": []})