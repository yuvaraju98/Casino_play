from flask import request
import logging
from app.utils import Util, RC_FAIL, RC_PASS, USERS, DEALERS, BETS
from app import app

logger = logging.getLogger(__name__)
# Globals
util = Util()


@app.route('/register/user', methods=['POST'])
def register_user():
    if not all(keys in request.json for keys in ['username', 'name']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.register_user(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Registration of task Successful, ID: {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Registration failed, error: {}".format(return_val[1]))
    return res


@app.route('/register/casino', methods=['POST'])
def register_casino():
    if not all(keys in request.json for keys in ['casino_name', 'location']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.register_casino(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Registration of task Successful, ID: {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Registration failed, error: {}".format(return_val[1]))

    return res


@app.route('/add_dealer', methods=['POST'])
def add_dealer():
    if not all(keys in request.json for keys in ['username', 'name', 'casino_id']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.register_dealer(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Registration of task Successful, ID: {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Registration failed, error: {}".format(return_val[1]))
    return res


@app.route('/entercasino', methods=['POST'])
def enter_casino():
    if not all(keys in request.json for keys in ['username', 'casino_id']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.enter_casino(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Entered Successful")
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))

    return res


@app.route('/recharge/user', methods=['POST'])
def recharge_balance():
    if not all(keys in request.json for keys in ['username', 'amount']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.recharge_user_balance(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Updation of task Successful, {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))

    return res


@app.route('/recharge/casino', methods=['POST'])
def recharge_casino_balance():
    if not all(keys in request.json for keys in ['casino_id', 'amount']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.recharge_casino_balance(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Updation of task Successful, {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))

    return res


@app.route('/list/users', methods=['GET'])
def list_users():

    return_val = util.display(USERS)
    if return_val[0]:
        res = util.make_response(RC_PASS, return_val[1])
    else:
        res = util.make_response(RC_FAIL, "Fetching failed, error: {}".format(return_val[1]))

    return res


@app.route('/list/dealers', methods=['POST'])
def list_dealers():

    if not all(keys in request.json for keys in ['casino_id']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.display(DEALERS, request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, return_val[1])
        else:
            res = util.make_response(RC_FAIL, "Fetching failed, error: {}".format(return_val[1]))

    return res


@app.route('/list/bets', methods=['POST'])
def list_bets():

    if not all(keys in request.json for keys in ['username']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.display(BETS, request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, return_val[1])
        else:
            res = util.make_response(RC_FAIL, "Fetching failed, error: {}".format(return_val[1]))

    return res


@app.route('/user/bet', methods=['POST'])
def user_bet():
    if not all(keys in request.json for keys in ['username', 'amount', 'game_id','number']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.add_bet_entry(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Placing bet successful Successful")
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))
    return res


@app.route('/game/start', methods=['POST'])
def start_game():
    if not all(keys in request.json for keys in ['dealer_id','casino_id']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.start_game(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Game start task Successful, id {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))
    return res


@app.route('/game/stop', methods=['POST'])
def stop_game():
    if not all(keys in request.json for keys in [ 'game_id']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.stop_game(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Stop of entries for game Successful")
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))
    return res


@app.route('/game/run', methods=['POST'])
def throw_ball():
    if not all(keys in request.json for keys in [ 'game_id']):
        res = util.make_response(RC_FAIL, "Missing Parameters.")
    else:
        return_val = util.throw_ball_and_update_balances(request.json)
        if return_val[0]:
            res = util.make_response(RC_PASS, "Game completed successful, {}".format(return_val[1]))
        else:
            res = util.make_response(RC_FAIL, "Updation failed, error: {}".format(return_val[1]))

    return res
