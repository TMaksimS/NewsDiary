import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
connect = redis.Redis(connection_pool=pool)
