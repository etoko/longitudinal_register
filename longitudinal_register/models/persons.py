from longitudinal_register.models import (
  Base, 
  )
from longitudinal_register.models.meta import BaseEntity

from sqlalchemy import (
  Column,
  Boolean,
  Integer,
  Text,
  Sequence,
  DateTime,
  String,
  ForeignKey,
  Table,
  UniqueConstraint,
  )   

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import (
  scoped_session,
  sessionmaker,
  )

from zope.sqlalchemy import ZopeTransactionExtension

class Person(Base, BaseEntity):

    __tablename__ = "persons"

    id = Column(u"id", Integer, Sequence("person_id_seq"), primary_key=True)
    surname = Column(u"surname", String(50), nullable = False)
    other_names = Column(u"other_names", String(100), nullable = False)
    gender = Column(u"gender", String(10), server_default = text("FEMALE"))
    #make date_of_birth optional for the mother
    dob = Column(u"dob", DateTime, server_default = text("now()")) 
    dob_estimated = Column(u"dob_estimated", String(20))
    status = Column(u"status", String(20)) # Entry point on workbook
    created_by = Column(u"created_by", ForeignKey("users.id"), server_default = text("now()"))
    created_on = Column(u"created_on", DateTime)
    modified_by = Column(u"modified_by", ForeignKey("users.id"), server_default = text("now()"))
    modified_on = Column(u"modified_on", DateTime)
 
    def __init__(self, *args, **kwargs):
        self.surname = kwargs.pop("surname", None)

class Patient(Base, BaseEntity):
    
    __tablename__ = "patients"

    id = Column(Integer, Sequence("patient_id_seq"), primary_key = True)
    person = Column(Integer, ForeignKey("persons.id"))    
    voided = Column(Boolean, default = False) 
    created_by = Column(u"created_by", ForeignKey("users.id"))
    created_on = Column(u"created_on", DateTime, server_default = text("now()"))
    modified_by = Column(u"modified_by", ForeignKey("users.id"))
    modified_on = Column(u"modified_on", DateTime, server_default = text("now()"))

class Relationship(Base, BaseEntity):
    
    __tablename__ = "relationship"
 
    id = Column(u"id", Integer, Sequence("relationship_id_seq"), primary_key=True)
    type = Column(u"type", ForeignKey("relationship_type.id"), nullable = False)
    person_a = Column(u"person_a", Integer, ForeignKey("person.id"), nullable = False)
    person_b = Column(u"person_b", Integer, ForeignKey("person.id"), nullable = False)
    created_by = Column(u"created_by", Integer, ForeignKey("users.id"), nullable = False)
    created_on = Column(u"created_on", DateTime, server_default = text("now()"))
    modified_by = Column(u"modified_by", Integer, ForeignKey("users.id"), \
            nullable = False)
    modified_on = Column(u"modified_on", DateTime, \
            server_default = text("now()"), server_onupdate=text("now()"))
    
class RelationshipType(Base, BaseEntity):
    
    __tablename__ = "relationship_type"

    id = Column(u"id", Integer, Sequence("relationship_type_id_seq"), \
            primary_key = True)
    name = Column(u"name", String(50), nullable = False)
    description = Column(u"description", String) 
