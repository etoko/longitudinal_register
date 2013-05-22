from datetime import datetime

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
from sqlalchemy.orm import ( 
     relationship, backref, 
     column_property,
     synonym,
     )
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.types import (
    Unicode, UnicodeText)
from sqlalchemy.sql.expression import text
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.security import (
  Allow,
  Everyone,
  authenticated_userid,
  remember,
  forget,
  )

import cryptacular.bcrypt

#from scm.util import dump_datetime
from . import Base, DBSession
from longitudinal_register.models.meta import BaseEntity

