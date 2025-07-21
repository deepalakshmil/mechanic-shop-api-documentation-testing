
from flask import Blueprint


inventories_bp = Blueprint("inventories_bp",__name__)

from . import routes