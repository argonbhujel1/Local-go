from app import db, socketio
from app.models.notification import Notification


class NotificationService:
    @staticmethod
    def notify_user(
        user_id: int,
        title: str,
        body: str = None,
        type: str = None,
        data: dict = None,
    ) -> Notification:
        n = Notification(
            user_id=user_id,
            title=title,
            body=body,
            type=type,
            data=data or {},
        )
        db.session.add(n)
        db.session.commit()

        socketio.emit(
            "notification",
            {
                "id": n.id,
                "title": title,
                "body": body,
                "type": type,
                "data": data,
            },
            room=f"user_{user_id}",
        )
        return n

    @staticmethod
    def mark_read(notification_id: int, user_id: int) -> bool:
        n = db.session.get(Notification, notification_id)
        if n and n.user_id == user_id:
            n.is_read = True
            db.session.commit()
            return True
        return False