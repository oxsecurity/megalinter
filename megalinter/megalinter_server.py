# !/usr/bin/env python3
"""
Start MegaLinter server
"""
import os
import subprocess
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

print ("MegaLinter Server starting...")
app = Flask(__name__)
api = Api(app)

subprocess_env_default = {**os.environ, "FORCE_COLOR": "0"}

parser = reqparse.RequestParser()
parser.add_argument('workspace')
parser.add_argument('debug')

running_processes = 0

class LintRequest(Resource):

    def get(self):
        global running_processes
        return {"runningProcesses": running_processes}

    def post(self):
        global running_processes
        running_processes += 1
        args = parser.parse_args()
        if not "workspace" in args:
            running_processes -= 1
            abort(404, message="Missing workspace property")
        workspace = args["workspace"] 
        print (f"Received request to lint workspace {args}")
        command = [
            "python",
            f"-m",
            "megalinter.run"
        ]
        subprocess_env = {**subprocess_env_default, "DEFAULT_WORKSPACE": workspace}
        if "debug" in args:
            subprocess_env["LOG_LEVEL"] = "DEBUG"
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
        running_processes -= 1
        return result

api.add_resource(LintRequest, '/lint_request')

if __name__ == '__main__':
    app.run(port=80,host='0.0.0.0',debug=True)