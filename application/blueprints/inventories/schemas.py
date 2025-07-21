from application.extensions import ma
from application.models import Inventory


#====Schema =====#
class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model= Inventory


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
