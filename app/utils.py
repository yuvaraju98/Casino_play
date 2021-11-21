import datetime
from datetime import datetime
from app import app
from bson.json_util import dumps
import random

# Globals
from app.database import db_session

from app.models import User, Casino, \
    Games, Casino_Balance, User_Gameplay, \
    Dealer, Bets

# return values
RC_PASS = 1
RC_FAIL = 0

# Display request types
USERS = 1
GAMES = 2
BETS = 3
DEALERS = 4

# Game status
GAME_OPEN = "OPEN"
GAME_CLOSED = "CLOSED"
GAME_COMPLETED = "COMPLETED"

# BETS status
BETS_LOST = "LOST"
BETS_WON = "WON"


class Util:

    def __init__(self):
        pass

    '''Common method to return response '''

    def make_response(self, status, response_data):
        return_dict = dict()
        if status == RC_PASS:
            return_dict['response'] = response_data
            return_dict['status'] = "success"
            response = app.response_class(
                response=dumps(return_dict, ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        else:
            return_dict['response'] = response_data
            return_dict['status'] = "fail"
            response = app.response_class(
                response=dumps(return_dict, ensure_ascii=False),
                status=400,
                mimetype='application/json'
            )
        return response

    ''' Register use : Adds entry to database'''

    def register_user(self, request_json):

        """ Register user """
        usr = User(
            request_json['username'],
            request_json['name'],
        )

        db_session.add(usr)

        """ Add the registered user into gameplay db"""
        gameplay_entry = User_Gameplay(
            user_id=request_json['username']
        )

        db_session.add(gameplay_entry)

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Registration failed {might already exist}"]

        return [True, usr.username]

    ''' Register casino: Adds casino entry to db'''

    def register_casino(self, request_json):

        """ Register casino """
        cur_entry = Casino(
            request_json['casino_name'],
            request_json['location'],
        )

        db_session.add(cur_entry)
        try:
            db_session.commit()
        except Exception as e:
            return [False, "Registration failed {might already exist}"]

        """Enter the casino to casino_balance ledger"""
        casino_entry = Casino_Balance(
            casino_id=cur_entry.id,
            amt=0
        )
        db_session.add(casino_entry)

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Registration failed {might already exist}"]

        return [True, cur_entry.id]

    ''' Register dealer : Adds dealer entry to db'''

    def register_dealer(self, request_json):

        """ Add dealer to db with corresponding to casino id"""
        cur_entry = Dealer(
            request_json['username'],
            request_json['name'],
            request_json['casino_id']
        )

        db_session.add(cur_entry)

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Registration failed {might already exist or casino doesnt exist}"]

        return [True, cur_entry.dealer_id]

    ''' Enter casino: updates current casino of user'''

    def enter_casino(self, request_json):

        """ Get the user gameplay row"""
        try:
            value = User_Gameplay.query.filter(User_Gameplay.user_id == request_json['username']).first()
        except Exception as e:
            return [False, "Failed while fetching data"]

        """Update user current casino id"""
        value.current_casino = request_json['casino_id']

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Failed to enter, reecheck id or already entered"]

        return [True, "Success"]

    ''' Recharge Balance : Updates user balance in db'''

    def recharge_user_balance(self, request_json):

        """ Get user object to updaate the balance"""
        try:
            value = User_Gameplay.query.filter(User_Gameplay.user_id == request_json['username']).first()
        except Exception as e:
            return [False, "Failed while fetching data"]

        if not value:
            return [False, "Failed while fetching data, recheck id"]

        value.balance_amount += request_json['amount']

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Failed adding data"]

        return [True, "Current balance {}".format(value.balance_amount)]

    ''' Recharge Balance : Updates casino balance in db'''

    def recharge_casino_balance(self, request_json):

        """ Get casino object to update balance"""
        try:
            value = Casino_Balance.query.filter(Casino_Balance.casino_id == request_json['casino_id']).first()
        except Exception as e:
            return [False, "Failed while fetching data"]

        if not value:
            return [False, "Casino not registered"]

        value.balance_amount += request_json['amount']

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Failed adding data"]

        return [True, "Current balance {}".format(value.balance_amount)]

    '''Add bet: Enters user bet into db'''

    def add_bet_entry(self, request_json):

        """ Get game object for gameid"""
        game_value = Games.query.filter(Games.id == request_json['game_id']).first()

        """ No game of requested game id present """
        if not game_value:
            return [False, "Game does not exists"]

        """ Handle case where game is already completed or game is closed for bets"""
        if game_value.status == GAME_COMPLETED:
            return [False, "Game has ended"]

        if game_value.status == GAME_CLOSED:
            return [False, "Bets for game has been closed"]

        """ Bet user gameplay object """
        try:
            usr_gameplay_value = User_Gameplay.query.filter(User_Gameplay.user_id == request_json['username']).first()
        except Exception as e:
            return [False, "Fetching usr details failed"]

        if not usr_gameplay_value:
            return [False, "User does not exists"]

        """ If user has not yet entered the casino """
        if usr_gameplay_value.current_casino != game_value.casino_id:
            return [False, "User has not entered correct casino for particular game"]

        """ User has insufficient balance"""
        if usr_gameplay_value.balance_amount < request_json['amount']:
            return [False, "User has insufficient Balance"]

        """ Deduct the amount from user balance"""
        usr_gameplay_value.balance_amount -= request_json['amount']

        """Add bet entries """
        cur_entry = Bets(
            user_id=request_json['username'],
            game_id=request_json['game_id'],
            amount=request_json['amount'],
        )
        db_session.add(cur_entry)
        cur_entry.bet_on_number = request_json['number']

        try:
            db_session.commit()
        except Exception as e:
            return [False, e]

        return [True, cur_entry.id]

    ''' start game: Adds game entry to db'''

    def start_game(self, request_json):

        """ Register and start the game"""
        cur_entry = Games(
            dealer_id=request_json['dealer_id'],
            casino_id=request_json['casino_id'],
            status=GAME_OPEN
        )

        db_session.add(cur_entry)

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Casino or dealer might not exist"]

        return [True, cur_entry.id]

    ''' stop game : Updates end time for the game in db'''

    def stop_game(self, request_json):

        """ Fetch game object"""
        try:
            value = Games.query.filter(Games.id == request_json['game_id']).first()
        except Exception as e:
            return [False, "Failed while fetching data"]

        if not value:
            return [False, "Game Id not found"]

        """ Gamr is not open, its completed or closed"""
        if value.status != GAME_OPEN:
            return [False, "Game already stopped/completed"]

        """ Update the values in the game"""
        setattr(value, 'end_time', datetime.now())
        setattr(value, 'status', GAME_CLOSED)

        try:
            db_session.commit()
        except Exception as e:
            return [False, e]

        return [True, "Success"]

    ''' Trows ball and update balances
        - Gets casino id and updates the current number to the game
        - Gets list of user id and amount from bets where user - won or lost
        - For each user id, we update the balance based on their game result
        - Casino balance is updated with lost game amount
        '''

    def throw_ball_and_update_balances(self, request_json):

        """ Generate random digit """
        random_digit = random.randint(1, 36)
        user_id_list = dict()
        casino_lost_amt = casino_won_amt = 0

        try:
            game_value = Games.query.filter(Games.id == request_json['game_id']).first()
        except Exception as e:
            return [False, "Error fetching game details"]

        """ Check if game object is present"""
        if not game_value:
            return [False, "Game Id not found"]

        """ If ball was already thrown fr=or the game"""
        if game_value.status == GAME_COMPLETED or game_value.status == GAME_OPEN:
            return [False, "Game is either Open/completed"]

        casino_id = game_value.casino_id
        setattr(game_value, 'thrown_number', random_digit)

        """ Get bets of won users"""
        try:
            bets_value = Bets.query.filter(Bets.game_id == request_json['game_id'], Bets.amount == random_digit).all()
        except Exception as e:
            return [False, "Failed while fetching won data"]

        user_id_list['won'] = bets_value

        """Get entries of lost users"""
        try:
            bets_value = Bets.query.filter(Bets.game_id == request_json['game_id'],
                                           Bets.amount != random_digit).all()
        except Exception as e:
            return [False, "Failed while fetching lost data"]

        user_id_list['lost'] = bets_value

        """ For each won user, bouble the amount"""
        for bets_obj in user_id_list['won']:
            value = User_Gameplay.query.filter(User_Gameplay.user_id == bets_obj.user_id).first()
            value.balance_amount += (bets_obj.amount * 2)
            casino_lost_amt += bets_obj.amount
            bets_obj.bet_status = BETS_WON

        '''We have already deducted the amount, hence no need to change here'''
        for bets_obj in user_id_list['lost']:
            casino_won_amt += bets_obj.amount
            bets_obj.bet_status = BETS_LOST

        try:
            output = Casino_Balance.query.filter(Casino_Balance.casino_id == casino_id).first()
        except Exception as e:
            return [False, "Failed while fetching data"]

        """ Update the casino balance"""
        updated_casino_balance = output.balance_amount + (casino_won_amt - casino_lost_amt)
        setattr(output, 'balance_amount', updated_casino_balance)

        '''Set status of current game to completed'''
        game_value.status = GAME_COMPLETED

        try:
            db_session.commit()
        except Exception as e:
            return [False, "Failed while commiting data"]

        return [True, "Success, number : {}".format(random_digit)]


    ''' Common display function : operates on display_type param'''
    def display(self, display_type, request_payload=None):

        output = {"result": []}
        if display_type == USERS:
            try:
                value = User.query.all()
            except Exception as e:
                return [False, "Failed fetching data"]
            for entries in value:
                output['result'].append(entries.asdict())

        elif display_type == DEALERS:
            try:
                value = Dealer.query.filter(Dealer.casino_id == request_payload['casino_id']).all()
            except Exception as e:
                return [False, e]

            for entries in value:
                output['result'].append(entries.asdict())

        elif display_type == BETS:
            ''' Get current casino of the user'''
            try:
                usr = User_Gameplay.query.filter(User_Gameplay.user_id == request_payload['username']).first()
            except Exception as e:
                return [False, "Failed fetching user data"]

            ''' Get all the games at current casino '''
            try:
                games = Games.query.filter(Games.casino_id == usr.current_casino, Games.status == GAME_OPEN).all()
            except Exception as e:
                return [False, e]

            for entries in games:
                output['result'].append(entries.asdict())

        return [True, output]
