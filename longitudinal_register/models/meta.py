#!/usr/bin/env python

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
from sqlalchemy.orm import relationship, backref, column_property
from sqlalchemy.orm.interfaces import MapperExtension
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.security import (
  Allow,
  Everyone,
  )

#from scm.util import dump_datetime
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class BaseExtension(MapperExtension):

    def before_insert(self, mapper, connection, instance):
        instance.created_on = datetime.now()

    def before_update(self, mapper, connection, instance):
        instance.updated_on = datetime.now()

class BaseEntity(object):
    __mapper_args__ = {
    "extension": BaseExtension
    }

