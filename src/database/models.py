from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    goal = Column(String)
    preferred_time = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    appointments = relationship("Appointment", back_populates="lead")

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    datetime = Column(DateTime)
    status = Column(String)  # scheduled, completed, cancelled
    notes = Column(String)
    lead = relationship("Lead", back_populates="appointments")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    plan_id = Column(String)
    status = Column(String)
    stripe_subscription_id = Column(String)
    started_at = Column(DateTime)
    next_billing_date = Column(DateTime)