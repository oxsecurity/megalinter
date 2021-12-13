# !/usr/bin/env python3
"""
Start MegaLinter server
"""
import os
import subprocess
import time
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

print("MegaLinter Server starting...")
app = Flask(__name__)
api = Api(app)

subprocess_env_default = {**os.environ, "FORCE_COLOR": "0"}

parser = reqparse.RequestParser()
parser.add_argument("workspace")
parser.add_argument("debug")

running_processes = 0
max_running_processes = 1


class LintRequest(Resource):
    def get(self):
        global running_processes
        return {"runningProcesses": running_processes}

    def post(self):
        args = parser.parse_args()
        print(f"Received request to lint workspace {args}")
        global running_processes
        running_processes += 1
        # Check max running processes has not been reached
        if running_processes > max_running_processes:
            running_processes -= 1
            abort(423, message="This server is already busy")
        # Missing workspacec property
        if not "workspace" in args:
            running_processes -= 1
            abort(400, message="Missing workspace property")
        workspace = args["workspace"]
        sarif_file_name = (
            "megalinter-report-"
            + os.environ.get("SINGLE_LINTER")
            + time.strftime("%Y%m%d-%H%M%S")
            + ".sarif"
        )
        # Lint command
        command = ["python", f"-m", "megalinter.run"]
        # Lint env variables
        subprocess_env = {
            **subprocess_env_default,
            "DEFAULT_WORKSPACE": workspace,
            "SARIF_REPORTER_FILE_NAME": workspace+"/megalinter-reports/"+sarif_file_name,
        }
        if "debug" in args:
            subprocess_env["LOG_LEVEL"] = "DEBUG"
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=subprocess_env,
        )
        return_code = process.returncode
        result = {
            "returnCode": return_code,
            "stdout": str(process.stdout),
            "sarifResult": sarif_file_name,
        }
        running_processes -= 1
        return result


api.add_resource(LintRequest, "/lint_request")

if __name__ == "__main__":
    app.run(port=80, host="0.0.0.0", debug=True)
