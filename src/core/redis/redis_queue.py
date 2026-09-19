from redis import Redis
from rq import Queue

redis_queue = Queue(
    connection=Redis(
        host="localhost",
        db=1,
    )
)

def get_queue():
    return redis_queue