# database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database.connection import Base

class Unit(Base):
    __tablename__ = "units"

    id        = Column(Integer, primary_key=True)
    beds      = Column(Integer, nullable=False)
    rent      = Column(Float,   nullable=False)
    location  = Column(String,  nullable=False)
    available = Column(Boolean, default=True)
    address   = Column(String,  nullable=True)
    amenities = Column(String,  nullable=True)

class Resident(Base):
    __tablename__ = "residents"

    id      = Column(Integer, primary_key=True)
    unit_id = Column(Integer, nullable=False)
    name    = Column(String,  nullable=False)
    email   = Column(String,  nullable=False, unique=True)
    phone   = Column(String,  nullable=True)

class Booking(Base):
    __tablename__ = "bookings"

    id         = Column(Integer, primary_key=True)
    unit_id    = Column(Integer, nullable=False)
    name       = Column(String,  nullable=False)
    email      = Column(String,  nullable=True)
    day        = Column(String,  nullable=False)
    time       = Column(String,  nullable=False)
    status     = Column(String,  default="confirmed")
    created_at = Column(DateTime, server_default=func.now())

class MaintenanceTicket(Base):
    __tablename__ = "maintenance_tickets"

    id          = Column(Integer, primary_key=True)
    unit_id     = Column(Integer, nullable=False)
    tenant_name = Column(String,  nullable=False)
    issue       = Column(Text,    nullable=False)
    priority    = Column(String,  nullable=False)
    email       = Column(String,  nullable=True)
    contact     = Column(String,  nullable=True)
    status      = Column(String,  default="open")
    created_at  = Column(DateTime, server_default=func.now())