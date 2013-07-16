import unittest
import transaction

from pyramid import testing

from longitudinal_register.models import DBSession


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from longitudinal_register.views import main_view
        request = testing.DummyRequest()
        info = main_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'longitudinal_longitudinal_longitudinal_register')
