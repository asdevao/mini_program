from flask import jsonify


class ResponseUtil:
    @staticmethod
    def success(message='', result=None, code=0):
        if result is None:
            result = {}
        return jsonify({
            'message': message,
            'result': result,
            'code': code,
            'type': 'success'
        })

    @staticmethod
    def error(message='', result=None, code=-1):
        if result is None:
            result = {}
        return jsonify({
            'message': message,
            'result': result,
            'code': code,
            'type': 'error'
        })
