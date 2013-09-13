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

from pyramid.security import (
    Allow,
    Authenticated,
    Everyone,
    )

from sqlalchemy import (
  Column,
  Integer,
  Text,
  )
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
from sqlalchemy.sql.expression import text


from sqlalchemy.orm import (
  backref,
  column_property,
  relationship,
  scoped_session,
  sessionmaker,
  synonym,
  )
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.orm.collections import attribute_mapped_collection
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.types import (
  Unicode,
  UnicodeText,
  )
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Person(Base):
    """
    Represents a person entity which directly represents a Patient
    """

    __tablename__ = "persons"

    id = Column(u"id", Integer, Sequence("person_id_seq"), primary_key=True)
    health_id = Column(u'health_id', String(20), unique = True)
    surname = Column(u"surname", String(50), nullable = False)
    other_names = Column(u"other_names", String(100), nullable = False)
    gender = Column(u"gender", String(10), default = "FEMALE")
    #make date_of_birth optional for the mother
    dob = Column(u"dob", DateTime, server_default = text("now()")) 
    dob_estimated = Column(Boolean, default=False)
    status = Column(u"status", String(20)) # Entry point on workbook
    location = Column(Integer, ForeignKey("locations.id"))
    created_by = Column(u"created_by", ForeignKey("users.id"))
    created_on = Column(u"created_on", DateTime, server_default = text("now()"))
    modified_by = Column(u"modified_by", ForeignKey("users.id"))
    modified_on = Column(u"modified_on", DateTime, server_default = text("now()"))
 
    def __init__(self, *args, **kwargs):
        self.surname = kwargs.pop("surname", None)


class Patient(Base):
    
    __tablename__ = "patients"

    id = Column(Integer, Sequence("patient_id_seq"), primary_key = True)
    person = Column(Integer, ForeignKey("persons.id"))
    voided = Column(Boolean, default = False)
    created_by = Column(u"created_by", ForeignKey("users.id"))
    created_on = Column(u"created_on", DateTime, server_default = text("now()"))
    modified_by = Column(u"modified_by", ForeignKey("users.id"))
    modified_on = Column(u"modified_on", DateTime, server_default = text("now()"))

class Relationship(Base):

    __tablename__ = "relationship"

    id = Column(u"id", Integer, Sequence("relationship_id_seq"), primary_key=True)
    type = Column(u"type", ForeignKey("relationship_type.id"), nullable = False)
    person_a = Column(u"person_a", Integer, ForeignKey("persons.id"), nullable = False)
    person_b = Column(u"person_b", Integer, ForeignKey("persons.id"), nullable = False)
    created_by = Column(u"created_by", Integer, ForeignKey("users.id"), nullable = True)
    created_on = Column(u"created_on", DateTime, server_default = text("now()"))
    modified_by = Column(u"modified_by", Integer, ForeignKey("users.id"), \
            nullable = False)
    modified_on = Column(u"modified_on", DateTime, \
            server_default = text("now()"), server_onupdate=text("now()"))

class RelationshipType(Base):

    __tablename__ = "relationship_type"

    id = Column(u"id", Integer, Sequence("relationship_type_id_seq"), \
            primary_key = True)
    name = Column(u"name", String(50), nullable = False)
    description = Column(u"description", String)


