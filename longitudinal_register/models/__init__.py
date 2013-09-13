#!env python
from datetime import datetime
import cryptacular.bcrypt
#
#from longitudinal_register.models.meta import Base
#from longitudinal_register.models.meta import DBSession
#from longitudinal_register.models.concepts import (
#  Concept,
#  ConceptAnswer,
#  ConceptClass,
#  ConceptDatatype,
#  )
#from longitudinal_register.models.visits import (
#  Visit,
#  VisitType,
#  )
#from longitudinal_register.models.locations import (
#  Location,
#  LocationType
#  )
#from longitudinal_register.models.persons import (
#  Patient,
#  Person,
#  Relationship,
#  RelationshipType,
#  )
#
#from longitudinal_register.models.users import (
#  User,
#  )

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


class BaseExtension(MapperExtension):

    def before_insert(self, mapper, connection, instance):
        instance.created_on = datetime.now()
        created_by = 1

    def before_update(self, mapper, connection, instance):
        instance.updated_on = datetime.now()
        modified_by = 1

class BaseEntity(object):
    __mapper_args__ = {
    "extension": BaseExtension
    }

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

user_groups = Table(u"user_groups", Base.metadata,
    Column(u"user_id", Integer, ForeignKey("users.id")),
    Column(u"group_id", Integer, ForeignKey("groups.id"))
    )

group_permissions = Table(u"group_permissions", Base.metadata,
    Column(u"group_id", Integer, ForeignKey("groups.id")),
    Column(u"permission_id", Integer, ForeignKey("permissions.id"))
    )

#visit_observations = Table(u"visit_observations", Base.metadata,
#    Column(u"visit", Integer, ForeignKey("visits.id")),
#    Column(u"observation", Integer, ForeignKey("observations.id"))
#    )

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

def hash_password(password):
    return unicode(crypt.encode(password))

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, "view"),
        (Allow, Authenticated, "post")
    ]

    def __init__(self, request):
        pass


class User(Base):
   
    __tablename__ = u"users"
    
    id = Column(u"id", Integer, Sequence("user_id_seq"), primary_key = True)
    username = Column(u"username", String(16), nullable = False, unique = True)
    first_name = Column(u"first_name", String(20), nullable = False)
    last_name = Column(u"last_name", String(50), nullable = False)
    other_name = Column(u"other_name", String(50), nullable = True)
    fullname = column_property(first_name + " " + last_name)
    email_address = Column(u"email_address", String(60))
#    password = Column(u"password", String(150), nullable = False)
    is_staff = Column(u"is_staff", Boolean, nullable = False)
    is_superuser = Column(u"is_superuser", Boolean, nullable = False)
    theme = Column(String(30), default = "claro", nullable = True)
    last_login = Column(u"last_login", DateTime, server_default = text("now()"),\
      nullable = False)
    created_by = Column(ForeignKey("users.id"))
    created_on = Column(u"created_on", DateTime, server_default = text("now()"))
    modified_by = Column(ForeignKey("users.id"))
    modified_on = Column(u"modified_on", DateTime,\
      server_default = text("now()"), server_onupdate = text("now()"))
    voided = Column(u"voided", Boolean, server_default = text("False"))
 
    groups = relationship("Group", secondary = user_groups, backref = "users")
    _password = Column('password', Unicode(60))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    def __init__(self, username, first_name, last_name, is_staff=False, \
                 is_active=False, is_superuser=False, last_login = datetime.now()):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = ""
        self.password = "editor"
        self.is_staff = is_staff
        self.is_active = is_active
        self.last_login = last_login

    def __repr__(self):
        return "<User: '%s', '%s', '%s'>" % (self.username, self.first_name, 
          self.last_name)

    __table_args__ = (UniqueConstraint("username", "email_address"),)

    @property
    def to_dict(self):
        """
        flatten model to dict. suitable for use in jsonification
        """
        return {
          "id":            self.id,
          "username":      self.username,
          "first_name":    self.first_name,
          "last_name":     self.last_name,
          "full_name":     self.fullname,
          "email_address": self.email_address,
          "password":      self.password,
          "is_staff":      self.is_staff,
          "is_superuser":  self.is_superuser,
          "theme":         self.theme,
          #"last_login":    dump_datetime(self.last_login),
          }
    
    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username == username).first()

    @classmethod
    def check_password(cls, username, password):
        user = cls.get_by_username(username)
        if not user:
            return False
        return crypt.check(user.password, password)
 

class Group(Base, BaseEntity):
    """
    Groups 
    """ 
    __tablename__ = "groups"
    
    id = Column("id", Integer, Sequence("group_id_seq"), primary_key = True)
    name = Column("name", String(30), nullable = False)
    created_by = Column("created_by", Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default = text("now()"))
    modified_by = Column(u"modified_by", Integer, ForeignKey("users.id"))
    modified_on = Column(u"modified_on", DateTime, 
      server_default = text("now()"), server_onupdate = text("now()"))

    permissions = relationship("Permission", secondary = group_permissions,
      backref = "groups")
    voided = Column(u"voided", Boolean, server_default = text("False"))

    __table_args__ = (UniqueConstraint("name"),)

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):    
        return "<Group %d %s>" % (self.id, self.name,)
    @property
    def to_dict(self):
        return {
               "id":            self.id,
               "name":          self.name,
               "created_by":    self.created_by,
               #"created_on": dump_datetime(self.created_on),
               "modified_by":   self.modified_by,
               #"modified_on": dump_datetime(self.modified_on)
               }





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
    relations = relationship("Relationship", \
        primaryjoin="Relationship.person_a==Person.id", \
        lazy="join"
        )
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
            nullable = True)
    modified_on = Column(u"modified_on", DateTime, \
            server_default = text("now()"), server_onupdate=text("now()"))

class RelationshipType(Base):

    __tablename__ = "relationship_type"

    id = Column(u"id", Integer, Sequence("relationship_type_id_seq"), \
            primary_key = True)
    name = Column(u"name", String(50), nullable = False)
    description = Column(u"description", String)




class Permission(Base, BaseEntity):
    """
    Permissions - List of priviliges that are contained in the system

    This lists all the permissions that a user/group has. By default, groups
    will be given a specified list of permissions. These can be overridden by
    custom assigning a user a given list of selected permissions.
    """
    __tablename__ = "permissions"

    id = Column(Integer, Sequence("permission_id_seq"), primary_key = True)
    name = Column(u"name", String(50), nullable = False, unique = True)
    description = Column(u"description", String(100), nullable = False)
    
    @property
    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
        }


class Location(Base):

    __tablename__ = "locations"

    id = Column(u"id", Integer, Sequence("locations_id_seq"), primary_key = True)
    name = Column(u"name", String(50))
    parent = Column(ForeignKey("locations.id"), nullable = True)
    location_type = Column(ForeignKey("location_types.id"), nullable =False)

class LocationType(Base):

    __tablename__= "location_types"

    id = Column(Integer, Sequence("location_type_id_seq"), primary_key = True)
    name = Column(String(50), nullable = False)
    notes = Column(Text, nullable = True)
   
    def __init__(self, name):
        self.name = name

class HealthUnit(Base):

    __tablename__ = "health_units"

    id = Column(Integer, Sequence("health_unit_seq_id"), primary_key = True)
    name = Column(String(100), nullable = False)
    description = Column(Text, nullable = True)
    gps = Column(String(70), nullable=True)
    location = Column(Integer, ForeignKey("locations.id"), nullable=False)
    location_id = relationship("Location", lazy="joined")
    health_unit_type_id = Column(Integer, ForeignKey("health_unit_types.id"))
    health_unit_type = relationship("HealthUnitType", lazy="joined")

    #def __init__():
   #     name = None
        #TODO add initialisation 

class HealthUnitType(Base):

    __tablename__ = "health_unit_types"

    id = Column(u"id", Integer, Sequence("health_unit_type_id_seq"), primary_key = True)
    name = Column(String(60), nullable = False)
    description = Column(Text, nullable = True)

class Concept(Base):

    __tablename__ = "concepts"
    __table_args = (UniqueConstraint("name"),)

    id = Column(Integer, Sequence("concept_id_seq"), primary_key = True)
    retired = Column(Boolean, nullable = False, default=False)
    name = Column(String(200))
    description = Column(u"description", Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default = text("now()"))
    modified_by = Column(Integer, ForeignKey("users.id"), nullable = True)
    modified_on = Column(DateTime, server_default = text("now()"),\
            server_onupdate = text("now()"))
    retired_by = Column(Integer, ForeignKey("users.id"), nullable = True)
    retired_on = Column(DateTime, nullable = True)
    retire_reason = Column(String(255), nullable = True)
    concept_answers = relationship("ConceptAnswer", lazy="joined", \
        primaryjoin="ConceptAnswer.concept==Concept.id")

class ConceptAnswer(Base):

    __tablename__ = "concept_answers"
    
    id = Column(Integer, Sequence("concept_answer_seq_id"), primary_key = True)
    concept = Column(Integer, ForeignKey("concepts.id"))
    concept_answer = Column(Integer, ForeignKey("concepts.id"))
    __table_args = (UniqueConstraint("concept", "answer_concept"),)
    

class ConceptClass(Base):

    __tablename__ = "concept_class" 
 
    id = Column(Integer, Sequence("concept_class_id_seq"), primary_key = True)
    name = Column(String(255), nullable = False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default=text("now()"))
    retired = Column(Boolean, default = False)
    retired_by = Column(Integer, ForeignKey("users.id")) 
    retired_on = Column(DateTime, server_default = text("now()"), nullable = True)
    retire_reason = Column(Text, nullable = True)

class ConceptDataType(Base):
    
    __tablename__ = "concept_datatype"
    __table_args = (UniqueConstraint("name"),)

    id = Column(Integer, Sequence("concept_datatype_id"), primary_key = True)
    name = Column(String(30), )
    description = Column(Text)
   

class Visit(Base):

    __tablename__ = "visits"

    id = Column(Integer, Sequence("visit_id_seq"), primary_key = True)
    form = Column(Integer, ForeignKey("forms.id"))
    patient = Column(Integer, ForeignKey("patients.id"), nullable = False)
    provider = Column(Integer, ForeignKey("users.id"))
    health_unit = Column(Integer, ForeignKey("health_units.id"))
    visit_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default = text("now()"))
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_on = Column(DateTime, server_default = text("now()"))
    voided = Column(Boolean, default = False)
    observations = relationship("Observation", order_by="Observation.id")

#class VisitType(Base):
#
#    __tablename__ = "visit_types"
#
#    id = Column(Integer, Sequence("visit_type_id_seq"), primary_key = True)
#    name = Column(String(50), nullable = False)
#    description = Column(Text)
#    created_by = Column(Integer, ForeignKey("users.id"))
#    created_on = Column(DateTime, server_default = text("now()"))
#    modified_by = Column(Integer, ForeignKey("users.id"))
#    modified_on = Column(DateTime, server_default = text("now()"))
#    voided = Column(Boolean, default = False)


class Observation(Base):

    __tablename__ = "observations"
    __table_args = (UniqueConstraint("visit", "concept"),)

    id = Column(Integer, Sequence("observation_id_seq"), primary_key = True)
    visit = Column(Integer, ForeignKey("visits.id"))
    date = Column(u"obs_date", DateTime)
    concept = Column(Integer, ForeignKey("concepts.id"))
    concept_value = Column(String(20), nullable = True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default = text("now()"))
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_on = Column(DateTime, server_default = text("now()"), \
            server_onupdate = text("now()"))
    voided = Column(Boolean, default = False) 


class Form(Base):

    __tablename__ = "forms"

    id = Column(Integer, Sequence("form_id_seq"), primary_key=True)
    name = Column(String(30))
    version = Column(String(20))
    description = Column(Text)
    form_concepts = relationship("FormConcept", lazy="joined", 
        primaryjoin="FormConcept.form == Form.id")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default = text("now()"))
    modified_by = Column(Integer, ForeignKey("users.id"))
    modified_on = Column(DateTime, server_default = text("now()"), \
        server_onupdate = text("now()"))


class FormConcept(Base):

    __tablename__ = "form_concepts"
    __table_args = (UniqueConstraint("form", "concept",))

    id = Column(Integer, Sequence("form_concept_id"), primary_key=True)
    form = Column(Integer, ForeignKey("forms.id"))
    concept = Column(Integer, ForeignKey("concepts.id"))

