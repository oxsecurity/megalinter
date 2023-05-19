'''
https://medium.com/@mike.p.moritz/using-docker-compose-to-deploy-a-lightweight-python-rest-api-with-a-job-queue-37e6072a209b
Run server: REDIS_HOST=localhost uvicorn megalinter.server:app (needs a redis server online on localhost:6379)
Run worker: cd /mnt/c/git/megalinter && rq worker --url redis://localhost:6379 megalinter_queue

docker build -t megalinter-server:latest -f server/Dockerfile .
'''
import logging
import logging.config
import os
from uuid import uuid1

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from megalinter import config

from megalinter.alpaca import alpaca
from redis_om import get_redis_connection
from rq import Queue
from server.server_worker import processAnalysisRequest
from server.types import AnalysisRequestInput, AnalysisRequestOutput

print("MegaLinter Server starting…")
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)  # type: ignore[attr-defined]
logger = logging.getLogger(__name__)
alpaca()

# Initialize FastAPI
server_id = "SRV_" + str(uuid1())
app = FastAPI(
    title="MegaLinter Server", version=config.get(None, "BUILD_VERSION", "DEV")
)
allow_origins = config.get_list(None, "CORS_ALLOW_ORIGINS", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.info("Fast API: " + app.version)
# Initialize redis connection
redis_host: str = os.environ.get("REDIS_HOST", "")
redis_port: int = int(os.environ.get("REDIS_PORT", 6379))
if redis_port != "":
    redis = get_redis_connection(
        host=redis_host, port=redis_port, decode_responses=True
    )
    logging.info("REDIS Connection: " + str(redis.info()))
    # Initialize redis Queue
    q = Queue("megalinter_queue", connection=redis)
    logging.info("REDIS Queue: " + str(q.name))
else:
    redis = None


# Post a new request to MegaLinter
@app.post(
    "/analysis",
    response_model=AnalysisRequestOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Requests a new analysis using repository url or snippet",
    description="""If the analysis initialization is successful, an id will be returned.
    If webHookUrl is provided, everytime a linter will be completed, the result will be sent to this HTTP webhook
    """,
)
async def request_analysis(
    item: AnalysisRequestInput,
) -> AnalysisRequestOutput:
    request_id = "RQ_" + str(uuid1())
    job = q.enqueue(
        processAnalysisRequest,
        item.dict(),
        request_id,
        server_id,
    )
    result = AnalysisRequestOutput(
        request_id=request_id, server_id=server_id, job_id=str(job.id)
    )
    return result
