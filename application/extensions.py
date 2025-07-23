
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

ma=Marshmallow()                             
limiter= Limiter(key_func=get_remote_address,default_limits=["10000 per day", "50 per minute"]) ## default for all routes in production
    ### Creating and instance of Limiter
    ### Global limit for all routes (can be overridden per route)
    ## limit all routes to 50 requests/minute by default 
    ## Adding the default_limits to the Limiter setup provides blanket protection to all routes, so you don’t need to decorate each one manually.

cache = Cache()