'''
https://medium.com/@mike.p.moritz/using-docker-compose-to-deploy-a-lightweight-python-rest-api-with-a-job-queue-37e6072a209b

DEV:
docker build -t megalinter-server:alpha --platform linux/amd64 -f server/Dockerfile-dev . && DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose -f server/docker-compose-dev.yml up

TEST:
docker pull --platform linux/amd64 ghcr.io/oxsecurity/megalinter-server:alpha && DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose -f server/docker-compose.yml up

'''
import logging
import logging.config
import os
from uuid import uuid1

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from rq import Queue
from server.types import AnalysisRequestInput, AnalysisRequestOutput

print("MegaLinter Server starting…")
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)  # type: ignore[attr-defined]
logger = logging.getLogger(__name__)

# Initialize FastAPI
server_id = "SRV_" + str(uuid1())
app = FastAPI(
    title="MegaLinter Server", version=os.environ.get("BUILD_VERSION", "DEV")
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.info("Fast API: " + app.version)
# Initialize redis connection
redis_host: str = os.environ.get("MEGALINTER_SERVER_REDIS_HOST", "megalinter_server_redis")
redis_port: int = int(os.environ.get("MEGALINTER_SERVER_REDIS_PORT", 6379))
redis_queue: str = os.environ.get("MEGALINTER_SERVER_REDIS_QUEUE","megalinter:queue:requests")
if redis_port != "":
    redis = Redis(host=redis_host, port=redis_port, db=0)
    logging.info("REDIS Connection: " + str(redis.info()))
    # Initialize redis Queue
    q = Queue(redis_queue, connection=redis)
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
        "server.server_worker.processAnalysisRequest",
        item.dict(),
        request_id,
        server_id,
    )
    result = AnalysisRequestOutput(
        request_id=request_id, server_id=server_id, job_id=str(job.id)
    )
    return result
