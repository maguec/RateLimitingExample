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

   epoch_time = int(time.time())
   pipe = r.pipeline()
   pipe.incrby("%s:hourly:%d" %(api, int(epoch_time/3600.0)*3600), 1)
   pipe.incrby("%s:daily:%d" %(api, int(epoch_time/86400.0)*86400), 1)
   pipe.get("%s:hourly:%d" %(api, int(epoch_time/3600.0)*3600))
   pipe.get("%s:daily:%d" %(api, int(epoch_time/86400.0)*86400))
   pipe.expire("%s:hourly:%d" %(api, int(epoch_time/3600.0)*3600), 3601)
   pipe.expire("%s:daily:%d" %(api, int(epoch_time/86400.0)*86400), 86401)
   res = pipe.execute()

   if int(res[2]) > CALL_PER_HOUR or int(res[3]) > CALL_PER_DAY:
       resp = Response("DATA Exceeded", status=429)
   else:
       resp = Response("DATA OK", status=200)

   resp.headers['X-Rate-Limit-Hour-Remaining'] = CALL_PER_HOUR - int(res[2])
   resp.headers['X-Rate-Limit-Day-Remaining'] = CALL_PER_DAY - int(res[3])
   return resp


if __name__ == '__main__':
   app.run()
