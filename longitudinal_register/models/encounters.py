#!env python
from longitudinal_register.models import Base

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
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
#encounter_observations = Table(u"encounter_observations",
#        Base.metadata,
#        Column(u"encounter", Integer, ForeignKey("encounters.id")),
#        Column(u"observations", Integer, ForeignKey("observations.id")))
