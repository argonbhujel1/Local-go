from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.payment_service import PaymentService

payments_api = Blueprint("payments_api", __name__)


@payments_api.route("/create", methods=["POST"])
@login_required
def create():
    data = request.get_json() or {}
    try:
        p = PaymentService.create_payment(
            job_id=data["job_id"],
            job_type=data.get("job_type", "RIDE"),
            customer_id=current_user.id,
            partner_id=data.get("partner_id"),
            amount=float(data["amount"]),
            platform_fee=float(data.get("platform_fee", 0)),
            method=data.get("method", "CASH"),
        )
        return jsonify({"ok": True, "payment_id": p.id})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@payments_api.route("/<int:pid>/customer-confirm", methods=["POST"])
@login_required
def customer_confirm(pid):
    data = request.get_json() or {}
    try:
        p = PaymentService.customer_confirm(pid, current_user.id, data.get("qr_reference"))
        return jsonify({"ok": True, "status": p.status})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@payments_api.route("/<int:pid>/partner-confirm", methods=["POST"])
@login_required
def partner_confirm(pid):
    if not current_user.partner:
        return jsonify({"ok": False, "error": "Not a partner"}), 403
    try:
        p = PaymentService.partner_confirm(pid, current_user.partner.id)
        return jsonify({"ok": True, "status": p.status})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400