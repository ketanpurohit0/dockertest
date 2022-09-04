from datetime import datetime
from redis import Redis
from redis.client import PubSub
from fastapi import FastAPI

app = FastAPI()
redis = Redis(host='redis', port=6379)
ps = redis.pubsub(ignore_subscribe_messages=True)

def some_topic_handler(some_topic_message):
    print("**", some_topic_message)

@app.on_event("startup")
async def on_startup():
    ps.subscribe({"some_topic":some_topic_handler})
    # get the subscribe message and throw it away
    ps.get_message()


@app.get("/")
def read_root():
    redis.incr('hits')
    redis.set('last', str(datetime.now()))
    counter = str(redis.get('hits'),'utf-8')
    #redis.bgsave()
    redis.publish("some_topic", f"a messsage {counter}")
    if int(counter) > 6:
        ps.unsubscribe("some_topic")

    m = ps.get_message()
    print(m)
    return f"This ****webpage has been viewed {counter} time(s), most recently {redis.get('last')}"



