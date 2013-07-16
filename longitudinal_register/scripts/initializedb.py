import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Location,
    LocationType,
    MyModel,
    Base,
    User,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    user = User("emmanuel.toko", "Emmanuel", "Toko")
    user.password = "12345"
    user.is_superuser = True

    location_type_none = LocationType("None")
    location_type_none.id = 10    

    location_types = (LocationType("District"), LocationType("County"), \
        LocationType("Sub County"), LocationType("Parish"), \
        LocationType("Village"), location_type_none)

    location = Location()
    location.name = "None"
    location.location_type = 10

    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(user)
        DBSession.add(model)
        DBSession.add_all(location_types)


    with transaction.manager:
        DBSession.add(location)
