# !/usr/bin/env python3
"""
Start MegaLinter server
"""
from flask import Flask
from flask_restful import Resource, Api

print ("MegaLinter Server starting...")
app = Flask(__name__)
api = Api(app)

class LintRequest(Resource):
    def post(self):
        result = {'lint_request': 'done'}
        return result

api.add_resource(LintRequest, '/lint_request')

if __name__ == '__main__':
    app.run(debug=True)