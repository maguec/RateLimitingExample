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
