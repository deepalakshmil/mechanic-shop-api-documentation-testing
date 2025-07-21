
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

ma=Marshmallow()
limiter= Limiter(key_func=get_remote_address,default_limits=["500 per hour"])  ### Creating and instance of Limiter
    ## limit all routes to 20 requests/hour by default ###creating and instance of Limiter
    ## Adding the default_limits to the Limiter setup provides blanket protection to all routes, so you don’t need to decorate each one manually.

cache = Cache()