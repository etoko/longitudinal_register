from pyramid.config import Configurator
from pyramid.events import BeforeRender
#from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

from longitudinal_register.models import (
    DBSession,
    Base,
    RootFactory,
    )
#from register import helpers

#def add_renderer_globals(event):
#    event['h'] = helpers

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # pyramid_beaker add-on
    session_factory = session_factory_from_settings(settings)
    authn_policy = SessionAuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()
    Base.metadata.bind = engine
 
    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        session_factory=session_factory,
        )

    config.add_static_view('static', 'static', cache_max_age=3600)
#    config.add_subscriber(add_renderer_globals, BeforeRender)
    # mako settings for file extension .html
    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    config.include(addroutes)
    config.scan()
    return config.make_wsgi_app()


def addroutes(config):
    config.add_route('main', '/')
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
 
    # patients
    config.add_route("patient_add_page", "/patient/add")
    config.add_route("person_save_view", "/person/save")
    config.add_route("patient_search", "/patient/search")
    config.add_route("patients_list_page", "/patients")
    config.add_route("patient_delete", "/patient/{health_id}/delete")
    config.add_route("patient_dashboard_page", "/patient/{health_id}")


    #visits
    config.add_route("visit_add", "/patient/{health_id}/visit/{form}/add")
    config.add_route("visit_edit", "/patient/{health_id}/visit/{form}/edit")
    config.add_route("visit_save", "/patient/{health_id}/visit/{form}/save")
    config.add_route("visit_list", "/patient/{health_id}/visit/list")

    #Locations
    config.add_route("locations_list", "/locations")
    config.add_route("location_add", "/location/add")
    config.add_route("location_add_view", "/location/new")

    #Health Units
    config.add_route("health_units_list", "/healthunits")
    config.add_route("health_unit_save_page", "/healthunit/add")
    config.add_route("health_unit_save", "/healthunit/save")
    config.add_route("health_unit_edit", "/healthunit/{name}/edit")
    config.add_route("health_unit_dashboard", "/healthunit/{name}")
