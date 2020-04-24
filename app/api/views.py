import logging
from . import mod
from . import proce
from flask import jsonify, request
from inc.retcode import RETCODE

logger = logging.getLogger(__name__)

@mod.route("/account/<account_id>", methods=["GET", "POST", "DELETE"])
def api_account(account_id):
    if not account_id or not account_id.isdigit():
        return jsonify(code=RETCODE.PARAMERR, error="param invalid")

    if request.method == "GET":
        data = proce.get_account_jsonify(account_id)
        return jsonify(code=RETCODE.OK, data=data)

    elif request.method == "POST":
        if not request.json.get('phone') and not request.json.get('nickname'):
            return jsonify(code=RETCODE.PARAMERR, error="param invalid")

        isok = proce.modify_account_info(account_id,
                    phone = request.json.get('phone'),
                    nickname = request.json.get('nickname'),
                    )
        if not isok:
            return jsonify(code=RETCODE.DATAERR, error="update error")
            
        return jsonify(code=RETCODE.OK, data={})

    elif request.method == "DELETE":
        proce.delete_account(account_id)
        return jsonify(code=RETCODE.OK, data={})


@mod.route("/accounts", methods=["GET"])
def get_all_account():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    accounts, total_count, next_page = proce.get_accounts(page=page, per_page=per_page)
    return jsonify(code=RETCODE.OK, data={
                    "accounts": accounts,
                    "total_count": total_count,
                    "next_page": next_page
                })


@mod.route("/add/account", methods=["post"])
def add_account():
    proce.add_account(
                phone = request.json.get('phone', ''),
                nickname = request.json.get('nickname', ''),
                )
    return jsonify(code=RETCODE.OK, data={})


@mod.route("/enable/account/<account_id>", methods=["post"])
def enable_account(account_id):
    if not account_id or not account_id.isdigit():
        return jsonify(code=RETCODE.PARAMERR, error="param invalid")
        
    isok = proce.enable_account(account_id)
    if not isok:
        return jsonify(code=RETCODE.DATAERR, error="update error")

    return jsonify(code=RETCODE.OK, data={})


@mod.route("/disable/account/<account_id>", methods=["post"])
def disable_account(account_id):
    if not account_id or not account_id.isdigit():
        return jsonify(code=RETCODE.PARAMERR, error="param invalid")

    isok = proce.disable_account(account_id)
    if not isok:
        return jsonify(code=RETCODE.DATAERR, error="update error")

    return jsonify(code=RETCODE.OK, data={})
