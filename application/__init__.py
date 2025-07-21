from flask import Flask
from application.extensions import ma,limiter,cache
from application.models import db
from application.blueprints.customers import customers_bp
from application.blueprints.mechanics import mechanics_bp
from application.blueprints.service_tickets import serviceTickets_bp
from application.blueprints.inventories import inventories_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URI = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'   # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URI,
    API_URL,
    config = {
        'app_name' : "Mechanic Shop API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')


    # Initialize extensions
    ma.init_app(app)  #Initializing Marshmallow extension onto our app
    db.init_app(app)  #adding our db extension to our app
    limiter.init_app(app)
    cache.init_app(app)  ## initializing cache on to our app


    # Register Blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(serviceTickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventories_bp, url_prefix='/inventories')
    app.register_blueprint(swaggerui_blueprint , url_prefix = SWAGGER_URI) # Registering our swagger blueprint



    return app