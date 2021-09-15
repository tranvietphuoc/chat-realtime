from flask import (
    Blueprint,
    render_template,
    session,
    copy_current_request_context,
    request,
)
from flask_socketio import (
    emit,
    join_room,
    leave_room,
    close_room,
    rooms,
    disconnect,
    SocketIO,
)
from threading import Lock


rt = Blueprint("rt", __name__)
thread = None
thread_lock = Lock()
async_mode = None
socket = SocketIO(async_mode=async_mode)


def background():
    "how to server generated events to clients"
    count = 0
    while True:
        socket.sleep(10)
        count += 1
        socket.emit(
            "my_response", {"data": "server generated event", "count": count}
        )


@rt.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html", async_mode=socket.async_mode)


@socket.event
def my_event(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": message["data"], "count": session["receive_count"]},
    )


@socket.event
def my_broadcast_event(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": message["data"], "count": session["receive_count"]},
        broadcast=True,
    )


@socket.event
def join(message):
    join_room(message["room"])
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {
            "data": "In rooms: " + ", ".join(rooms()),
            "count": session["receive_count"],
        },
    )


@socket.event
def leave(message):
    leave_room(message["room"])
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {
            "data": "In rooms: " + ", ".join(rooms()),
            "count": session["receive_count"],
        },
    )


@socket.on("close_room")
def on_close_room(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {
            "data": "Room" + message["room"] + "is closing.",
            "count": session["receive_count"],
        },
        to=message["room"],
    )
    close_room(message["room"])


@socket.event
def my_room_event(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": message["data"], "count": session["receive_count"]},
        to=message["room"],
    )


@socket.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": "Disconnected", "count": session["receive_count"]},
        callback=can_disconnect,
    )


@socket.event
def my_ping():
    emit("my_pong")


@socket.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socket.start_background_task(background)

    emit("my_response", {"data": "Connected", "count": 0})


@socket.on("disconnect")
def test_disconnect():
    print("Client disconnected", request.sid)
