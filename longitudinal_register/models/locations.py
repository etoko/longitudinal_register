#!/usr/bin/env python

from sqlalchemy import (
   Column,
   Integer,
   Sequence,
   String,
   Text,
   )
from sqlalchemy.schema import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

Base = declarative_base()

class Location(Base):

    __tablename__ = "locations"

    id = Column(u"id", Integer, Sequence("user_id_seq"), primary_key = True)
    name = Column(u"name", String(50))
    parent = Column(ForeignKey("locations.id"), nullable = True)
    l_type = Column(ForeignKey("location_types.id"), nullable =True)

#    def __init__():
        #TODO add initialisation 

class LocationType(Base):

    __tablename__= "location_types"

    id = Column(Integer, Sequence("location_type_id_seq"), primary_key = True)
    name = Column(String(50), nullable = False)
    notes = Column(Text, nullable = True)

class HealthUnit(Base):

    __tablename__ = "health_units"

    id = Column(Integer, Sequence("health_unit_seq_id"), primary_key = True)
    name = Column(String(100), nullable = False)
    notes = Column(Text, nullable = True, default = "")

    def __init__():
        name = None
        #TODO add initialisation 
