from datetime import datetime
from redis import Redis
from fastapi import FastAPI

app = FastAPI()
redis = Redis(host='redis', port=6379)


@app.get("/")
def read_root():
    redis.incr('hits')
    redis.set('last', str(datetime.now()))
    counter = str(redis.get('hits'),'utf-8')
    #redis.bgsave()
    return f"This *webpage has been viewed {counter} time(s), most recently {redis.get('last')}"



