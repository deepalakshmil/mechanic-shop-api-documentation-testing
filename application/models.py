from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List


# Create a base class for our models
class Base(DeclarativeBase):
    pass

#Instantiate your SQLAlchemy database and Initialize Extensions:
db=SQLAlchemy(model_class=Base)


class Customer(Base):
    __tablename__ = 'customers'


    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(db.String(255),nullable=False)
    email: Mapped[str]=mapped_column(db.String(400),nullable=False,unique=True)
    password: Mapped[str]=mapped_column(db.String(300),nullable=False)
    address: Mapped[str]=mapped_column(db.String(300),nullable=False)
    phone: Mapped[str]=mapped_column(db.String(120),nullable=False)
    salary: Mapped[float]=mapped_column(db.Float(), nullable=False)

     # This relates one Customer to many Service_tickets.
    services: Mapped[List['Service_tickets']] = db.relationship(back_populates ='customer')
    

# Association Table

mechanic_services = db.Table('mechanic_services', Base.metadata,
                   db.Column('mechanic_id',db.ForeignKey('mechanics.id')),
                   db.Column('service_id',db.ForeignKey('service_tickets.id')))


#Creating a Model for a Junction Table

class ServiceInventory(Base):
    __tablename__ = 'service_inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'), nullable=False)
    inventory_id : Mapped[int] = mapped_column(db.ForeignKey('inventories.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

     # Optional: relationships back to parent tables
    service_ticket: Mapped['Service_tickets'] = db.relationship(back_populates ='service_inventories')
    inventory: Mapped['Inventory'] = db.relationship(back_populates ='service_inventories')

class Mechanics(Base):
    __tablename__ = 'mechanics'


    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(db.String(255),nullable=False)
    address: Mapped[str]=mapped_column(db.String(300),nullable=False)
    email: Mapped[str]=mapped_column(db.String(400),nullable=False,unique=True)
    phone: Mapped[str]=mapped_column(db.String(100),nullable=False)

      #creating a many-to-many relationship to Mechanics through or association table mechanic_services
    services: Mapped[List['Service_tickets']] = db.relationship(secondary=mechanic_services, back_populates='mechanics')

class Service_tickets(Base):
    __tablename__ = 'service_tickets'


    id: Mapped[int]=mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(255),nullable=False)
    service_date: Mapped[date]= mapped_column(db.Date)
    customer_issue: Mapped[str] = mapped_column(db.String(350),nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'),nullable=False)

       #creating a many-to-one relationship to Customer table
    customer: Mapped['Customer'] = db.relationship(back_populates='services')

      #creating a many-to-many relationship to Service_tickets through or association table mechanic_services
    mechanics: Mapped[List['Mechanics']] = db.relationship(secondary=mechanic_services, back_populates='services')  
     
    #    #Creating a relationship between Service_tickets and inventory through service_inventory.
    service_inventories: Mapped[List['ServiceInventory']] = db.relationship(back_populates ='service_ticket')

class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225),nullable= False)
    price: Mapped[float] = mapped_column(db.Float(), nullable= False)
    
      #Creating a relationship between Inventory and Service_tickets through service_inventory.
    service_inventories: Mapped[List['ServiceInventory']] = db.relationship(back_populates ='inventory')