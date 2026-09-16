from flask import request
from flask_login import current_user
from flask_socketio import join_room, leave_room, emit

from app import socketio, db
from app.models.partner import Partner
from app.models.system import GPSLocation
from datetime import datetime


@socketio.on("connect")
def on_connect():
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        if current_user.is_partner and current_user.partner:
            join_room("partners_online")
            join_room(f"partner_{current_user.partner.id}")


@socketio.on("disconnect")
def on_disconnect():
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")


@socketio.on("join_job")
def on_join_job(data):
    job_id = data.get("job_id")
    if job_id:
        join_room(f"ride_{job_id}")
        join_room(f"job_{job_id}")


@socketio.on("leave_job")
def on_leave_job(data):
    job_id = data.get("job_id")
    if job_id:
        leave_room(f"ride_{job_id}")
        leave_room(f"job_{job_id}")


@socketio.on("partner_location")
def on_partner_location(data):
    """Partner sends live GPS while on a job or online."""
    if not current_user.is_authenticated or not current_user.partner:
        return
    partner = current_user.partner
    lat = data.get("latitude")
    lng = data.get("longitude")
    if lat is None or lng is None:
        return

    partner.last_location_lat = float(lat)
    partner.last_location_lng = float(lng)
    partner.last_location_at = datetime.utcnow()
    db.session.commit()

    job_id = data.get("job_id")
    if job_id:
        loc = GPSLocation(
            job_id=job_id,
            partner_id=partner.id,
            latitude=float(lat),
            longitude=float(lng),
            accuracy=data.get("accuracy"),
            heading=data.get("heading"),
            speed=data.get("speed"),
            recorded_at=datetime.utcnow(),
        )
        db.session.add(loc)
        db.session.commit()

        # Broadcast only to the job room (customer)
        emit(
            "partner_location_update",
            {
                "job_id": job_id,
                "latitude": float(lat),
                "longitude": float(lng),
                "heading": data.get("heading"),
                "speed": data.get("speed"),
                "timestamp": datetime.utcnow().isoformat(),
            },
            room=f"job_{job_id}",
        )


@socketio.on("chat_message")
def on_chat_message(data):
    from app.models.notification import Message

    if not current_user.is_authenticated:
        return
    job_id = data.get("job_id")
    receiver_id = data.get("receiver_id")
    body = (data.get("body") or "").strip()
    if not body or not receiver_id:
        return

    msg = Message(
        job_id=job_id,
        sender_id=current_user.id,
        receiver_id=int(receiver_id),
        body=body,
    )
    db.session.add(msg)
    db.session.commit()

    payload = {
        "id": msg.id,
        "job_id": job_id,
        "sender_id": current_user.id,
        "receiver_id": int(receiver_id),
        "body": body,
        "created_at": msg.created_at.isoformat(),
    }
    emit("chat_message", payload, room=f"user_{receiver_id}")
    emit("chat_message", payload, room=f"user_{current_user.id}")