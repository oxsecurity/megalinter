# !/usr/bin/env python3
"""
Start MegaLinter server
"""
import os
import subprocess
from flask import Flask
from flask_restful import Resource, Api, reqparse

print ("MegaLinter Server starting...")
app = Flask(__name__)
api = Api(app)

subprocess_env_default = {**os.environ, "FORCE_COLOR": "0"}

parser = reqparse.RequestParser()
parser.add_argument('workspace')

class LintRequest(Resource):
    def post(self):
        args = parser.parse_args()
        if not "workspace" in args:
            return {"errorMessage": "Missing workspace property"}
        workspace = args["workspace"] 
        print (f"Received request to lint workspace {args}")
        command = [
            "python",
            f"-m",
            "megalinter.run"
        ]
        subprocess_env = {**subprocess_env_default, "DEFAULT_WORKSPACE": workspace}
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=subprocess_env
        )
        return_code = process.returncode
        result = {
            'returnCode': return_code, 
            'stdout': str(process.stdout)
            }
        return result

api.add_resource(LintRequest, '/lint_request')

if __name__ == '__main__':
    app.run(debug=True)