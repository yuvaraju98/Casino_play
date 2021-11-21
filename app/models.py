from datetime import datetime
from app.database import init_db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base
import time

class User(Base):
    __tablename__ = 'User'
    username = Column(String(50), primary_key=True, unique=True)
    name = Column(String(50))

    def __init__(self, username, name):
        self.name = name
        self.username = username

    def asdict(self):
        output_dict = {
            "username": self.username,
            "name": self.name,
        }
        return output_dict


class Casino(Base):
    __tablename__ = 'Casino'
    id = Column(Integer, primary_key=True, autoincrement=True)
    casino_name = Column(String(50))
    location = Column(String(50))

    def __init__(self, casino_name, location):
        self.casino_name = casino_name
        self.location = location


class Dealer(Base):
    __tablename__ = "Dealers"
    dealer_id = Column(String(50), primary_key=True, unique=True)
    casino_id = Column(String(50), ForeignKey('Casino.id'), nullable=False)

    def __init__(self, username, name, casino_id):
        User(username, name)
        self.casino_id = casino_id
        self.dealer_id = username

    def asdict(self):
        output_dict = {
            "dealer_id": self.dealer_id,
        }
        return output_dict


class Games(Base):
    __tablename__ = 'Games'
    id = Column(Integer, primary_key=True, autoincrement=True)
    casino_id = Column(String(50), ForeignKey('Casino.id'))
    dealer_id = Column(String(50), ForeignKey('Dealers.dealer_id'))
    start_time = Column(DateTime, default=datetime.now())
    end_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50))
    thrown_number = Column(Integer, default=0)

    def __int__(self, dealer_id, casino_id, status):
        self.casino_id = casino_id
        self.dealer_id = dealer_id
        self.status = status

    def asdict(self):
        output_dict = {
            "game_id": self.id,
            "casino_id": self.casino_id,
            "start_time": self.start_time
        }
        return output_dict


class Bets(Base):
    __tablename__ = 'Bets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer)
    time = Column(DateTime, default=datetime.now())
    user_id = Column(String(50), ForeignKey('User.username'))
    game_id = Column(Integer, ForeignKey('Games.id'))
    bet_status = Column(Integer, default=0)
    bet_on_number = Column(Integer, default=0)

    def __int__(self,  user_id, game_id, amount):
        self.game_id = game_id
        self.user_id = user_id
        self.amount = amount


class User_Gameplay(Base):
    __tablename__ = 'User_gameplay'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(String(50), ForeignKey('User.username'), unique=True)
    current_casino = Column(String(50), ForeignKey('Casino.id'))
    balance_amount = Column(Integer, default=0)

    def __init__(self, user_id, casino_id=None):
        self.user_id = user_id
        self.current_casino = casino_id


class Casino_Balance(Base):
    __tablename__ = 'Casino_balance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    casino_id = Column(String(50), ForeignKey('Casino.id'),  unique=True)
    balance_amount = Column(Integer, default=0)

    def __init__(self, casino_id, amt):
        self.casino_id = casino_id
        self.balance_amount = amt


init_db()
