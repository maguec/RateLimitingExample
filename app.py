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

   # set the points for this route to 4
   ROUTE_SCORE = 4

   r = redis.Redis(host='localhost', port=6379, db=0)

   api = request.headers.get('X-API-Key')
   if api == None:
       resp = Response("Please set the X-API-Key header", status=401)
       return resp

   epoch_ms = int(time.time()*1000)
   pipe = r.pipeline()

   pipe.zremrangebyscore("%s:hourly" %(api), 0,  epoch_ms - 360000)
   pipe.zrange("%s:hourly" %(api), 0, -1)
   pipe.zadd("%s:hourly" %(api), {"%d:%d" %(epoch_ms, ROUTE_SCORE): epoch_ms})
   pipe.expire("%s:hourly" %(api), 3600001)

   pipe.zremrangebyscore("%s:daily" %(api), 0,  epoch_ms - 86400000)
   pipe.zrange("%s:daily" %(api), 0, -1)
   pipe.zadd("%s:daily" %(api), {"%d:%d" %(epoch_ms, ROUTE_SCORE): epoch_ms})
   pipe.expire("%s:daily" %(api), 86400000)

   res = pipe.execute()

   hour_score = sum(int(i.decode("utf-8").split(':')[-1]) for i in res[1])
   day_score = sum(int(i.decode("utf-8").split(':')[-1]) for i in res[5])


   if hour_score > CALL_PER_HOUR or day_score > CALL_PER_DAY:
       resp = Response("DATA Exceeded", status=429)
   else:
       resp = Response("DATA OK", status=200)

   resp.headers['X-Rate-Limit-Hour-Remaining'] = CALL_PER_HOUR - hour_score
   resp.headers['X-Rate-Limit-Day-Remaining'] = CALL_PER_DAY - day_score
   return resp


if __name__ == '__main__':
   app.run()
