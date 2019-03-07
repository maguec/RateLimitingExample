# Flask Simple Rate limiting Example


## Starup docker container if you want to test locally

```
docker run --rm -p 6379:6379 redis
```

## Install python requirements

```
pip3 install -r requirements.txt
```

## Start the flask app

```
python3 app.py 
```

## Testing

```
curl -v -H "X-API-Key: testkey1" localhost:5000/throttle
```

Run the above command 7 times.  On the 7th run it should return an HTTP status code of 429


## Details

The application will return the following headers

```
 X-Rate-Limit-Hour-Remaining: 5
 X-Rate-Limit-Day-Remaining: 9
```

That will let the user know how many requests they have remaining before the run over the limit

Data is stored in redis as a sorted set

```
> "ZRANGE" "testkey2:hourly" "0" "-1"  WITHSCORES
1) "1551987157790:4"
2) "1551987157790"
3) "1551987158414:4"
4) "1551987158414"
5) "1551987159051:4"
6) "1551987159051"
7) "1551987159612:4"
8) "1551987159612"
```

The element is the TIMESTAMP:POINTS and we sum the points returned to ensure that we do not go over the rate limiting totals per day and hour

The hourly key will expire 1 hour and 1 second after the last update in that bucket and the daily will expire in 24 hours and 1 second to keep the keyspace from filling up
