from flask import Flask, render_template, request, Response
import redis
import time

CALL_PER_HOUR = 6
CALL_PER_DAY  = 10

app = Flask(__name__)

@app.route('/')
def hello_root():
   resp = Response("OK")
   return resp

@app.route('/throttle')
def throttle():
   r = redis.Redis(host='localhost', port=6379, db=0)

   api = request.headers.get('X-API-Key')
   if api == None:
       resp = Response("Please set the X-API-Key header", status=401)
       return resp

   epoch_ms = int(time.time()*1000)
   pipe = r.pipeline()

   pipe.zremrangebyscore("%s:hourly" %(api), 0,  epoch_ms - 360000)
   pipe.zrange("%s:hourly" %(api), 0, -1)
   pipe.zadd("%s:hourly" %(api), {epoch_ms: epoch_ms})
   pipe.expire("%s:hourly" %(api), 3600001)

   pipe.zremrangebyscore("%s:daily" %(api), 0,  epoch_ms - 86400000)
   pipe.zrange("%s:daily" %(api), 0, -1)
   pipe.zadd("%s:daily" %(api), {epoch_ms: epoch_ms})
   pipe.expire("%s:daily" %(api), 86400000)

   res = pipe.execute()

   print(res)

   if len(res[1]) > CALL_PER_HOUR or len(res[5]) > CALL_PER_DAY:
       resp = Response("DATA Exceeded", status=429)
   else:
       resp = Response("DATA OK", status=200)

   resp.headers['X-Rate-Limit-Hour-Remaining'] = CALL_PER_HOUR - len(res[1])
   resp.headers['X-Rate-Limit-Day-Remaining'] = CALL_PER_DAY - len(res[5])
   return resp


if __name__ == '__main__':
   app.run()
