import os
from app import create_app, socketio, db

app = create_app(os.environ.get("FLASK_ENV", "development"))


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "app": app}


if __name__ == "__main__":
    # Use socketio.run for WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config.get("DEBUG", True),
        allow_unsafe_werkzeug=True,
    )