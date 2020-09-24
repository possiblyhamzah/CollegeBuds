import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import User, Room
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

socketio = SocketIO(app)

@app.route("/")
def index():
    # If the user is logged in, redirect to the chatlist page
    if "username" in session:
        if "chat_id" in session:
            return redirect(url_for('chatroom', chat_id=session["chat_id"]))
        return redirect(url_for('chatroomlist'))
    
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form info
        username = request.form.get("name")
        password = request.form.get("password")
        
        # Check if user exists
        account = User.query.filter_by(username = username).first()
        if account is None:
            return render_template("error.html", message = "This account does not exist.")
        else:
            
            # Check if passwords match
            passw = User.query.filter_by(username = username).first().password
            check_password = check_password_hash(passw, password)

            if check_password == False:
                return render_template("error.html", message = "Wrong password.")
            session['username'] = username
        return redirect(url_for('chatroomlist'))
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":

        # Get form info
        username = request.form.get("name")
        password = request.form.get("password")
        
        # Check if the username is unique
        rows = User.query.filter_by(username = username).first()

        if rows == None:
        
            # Create user
            user=User(
                username=username,
                password= generate_password_hash(password),
                rooms='',
                room_ids=''
            )
            db.session.add(user)
            db.session.commit()
            

            
            session['username'] = username
            return redirect(url_for('chatroomlist'))
        else:
            return render_template("index.html", message="This username has already been taken.")

    return render_template("index.html")
 
    

@app.route("/chatrooms", methods=["POST", "GET"]) 
def chatroomlist():
    
    # Get the list of rooms the user has joined
    chatlist = User.query.filter_by(username = session['username']).first().rooms

    if chatlist != '':
        chatlist = chatlist.split(' : ')
    
    
    chats = Room.query.all()

    # Get the ids of the rooms
    room_ids = User.query.filter_by(username = session['username']).first().room_ids

    if room_ids != '':
        room_ids = room_ids.split(' : ')
    return render_template("chatlist.html", chats=chats, chatlist=chatlist, room_ids=room_ids)

@app.route("/chatroom/<int:chat_id>", methods=["GET"]) 
def chatroom(chat_id):
    session["chat_id"] = chat_id
    return render_template("chatroom.html", user_name=session["username"])


@socketio.on("submit channel")
def submit_channel(data):

    chat_id = int(data['selection'])

    # Get the rooms the user has joined, and add the room to the list

    rooms = User.query.filter_by(username = session['username']).first().rooms

    if rooms != '':
        rooms += ' : '
    
    
    room_name = Room.query.filter_by(id = chat_id).first().name
    rooms += room_name

    room_ids = User.query.filter_by(username = session['username']).first().room_ids

    if room_ids != '':
        room_ids += ' : '
    room_ids += str(chat_id)
    
    user = User.query.filter_by(username = session['username']).first()
    user.rooms = rooms 
    user.room_ids = room_ids

    db.session.commit()
    emit("cast channel", {"selection": room_name, "chat_id": chat_id}, broadcast=True)

@socketio.on("submit message")
def message(data):
    
    # Get message info

    selection = data["selection"]
    time = datetime.now().strftime("%d-%m-%Y %H:%M")
    response = {"selection": selection, "time": time, "user_name": session["username"]}


    # Get the list of messages

    name = Room.query.filter_by(id = session['chat_id']).first().name
    
    messagelist = json.loads(Room.query.filter_by(name = name).first().messages)

    # Keep the number of messages to 100 
    if len(messagelist) == 100:
        del messagelist[0]


    # Add the messages to the existing list of messages

    messagelist.append(response)
    
    room = Room.query.filter_by(name = name).first()
    room.messages = json.dumps(messagelist)

    db.session.commit()
    emit("cast message", {**response, **{"chat_id": str(session["chat_id"])}}, broadcast=True)

@socketio.on("submit priv channel")
def submit_priv_channel(data):

    # If a user adds a channel name, add the name of the channel to the channel list as well to the user's list of joined channels

    room_name = data['selection']
    newroom=Room(
        name = room_name,
        messages = '[]'
    )
    db.session.add(newroom)
    db.session.commit()
    
    chat_id = Room.query.filter_by(name = room_name).first().id

    rooms = User.query.filter_by(username = session['username']).first().rooms


    if rooms != '':
        rooms += ' : '
    

    rooms += room_name

    
    room_ids = User.query.filter_by(username = session['username']).first().room_ids

    if room_ids != '':
        room_ids += ' : '
    room_ids += str(chat_id)

    
    user = User.query.filter_by(username = session['username']).first()
    user.rooms = rooms 
    user.room_ids = room_ids

    db.session.commit()
    emit("cast priv channel", {"selection": room_name, "chat_id": chat_id}, broadcast=True)



@app.route("/list", methods=["POST"])
def listmessages():

    # Get the list of messages
        
    messagedict = json.loads(Room.query.filter_by(id = session['chat_id']).first().messages)

    return jsonify({**{"message": messagedict}, **{"chat_id": session["chat_id"]}})

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5004)
