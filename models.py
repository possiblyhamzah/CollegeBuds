from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    rooms = db.Column(db.String())
    room_ids = db.Column(db.String())

    

    def __init__(self, username, password, rooms, room_ids):
        self.username = username
        self.password = password
        self.rooms = rooms
        self.room_ids = room_ids

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'username': self.username,
            'password': self.password,
            'rooms': self.rooms,
            'room_ids': self.room_ids

        }

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    messages = db.Column(db.String())
    
    

    def __init__(self, name, messages):
        self.name = name
        self.messages = messages

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'messages': self.messages
        }