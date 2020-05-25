import flask
import json
import os
import flask_cors
from data_fetching_db import *
from pymysql.err import InternalError

svr = flask.Flask(__name__)
svr.config['JSON_AS_ASCII'] = False
flask_cors.CORS(svr, resources=r'/*')


@svr.route('/request_info', methods=['POST'])
def get_info():
    print("received")
    if flask.request.method == 'POST':
        a = flask.request.get_data()
        dict1 = json.loads(a)

        req = dict1['request']
        if req == 'boss':
            boss_id = dict1['boss_id']
            mode = dict1['mode']
            try:
                res = fetch_boss(boss_id, mode)
            except InternalError:
                res = {}
        elif req == 'member_list':
            res = fetch_member()

        print(res)
        response = flask.make_response(flask.jsonify(json.dumps(res)))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        return response
    return ''


if __name__ == '__main__':
    svr.run(debug=True, port=9960)
