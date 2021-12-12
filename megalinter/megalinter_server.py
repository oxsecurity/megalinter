# !/usr/bin/env python3
"""
Start MegaLinter server
"""
import os
import subprocess
from flask import Flask
from flask_restful import Resource, Api

print ("MegaLinter Server starting...")
app = Flask(__name__)
api = Api(app)

subprocess_env = {**os.environ, "FORCE_COLOR": "0"}

class LintRequest(Resource):
    def post(self):
        command = [
            "python",
            f"-m",
            "megalinter.run"
        ]
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