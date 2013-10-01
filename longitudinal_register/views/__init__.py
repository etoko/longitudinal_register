import transaction

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.security import (
    authenticated_userid,
    forget,
    remember,
    )


from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import eagerload
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import subqueryload_all
from sqlalchemy.exc import DBAPIError

from longitudinal_register import models


@view_config(permission="view", route_name='main', renderer='dashboard.html')
def main_view(request):
    list_of_visits = []
    try:
        with transaction.manager:
            visits = models.DBSession.query(models.Visit).\
                options(joinedload("*")).\
                order_by(models.Visit.visit_date.desc()).slice(0, 10).all()
            #for visit in visits:
                #visit.health_unit = models.DBSession.query(models.HealthUnit).\
                #    get(visit.health_unit)
                #visit.health_unit = models.DBSession.query(models.HealthUnit).get(visit.health_unit).name
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'visits': visits, 'page': 'Dashboard'}


@view_config(permission='view', route_name='login')
def login_view(request):
    main_view = request.route_url('main')
    came_from = request.params.get('came_from', main_view)

    post_data = request.POST
    if 'submit' in post_data:
        login = post_data['login']
        password = post_data['password']

        if User.check_password(login, password):
            headers = remember(request, login)
            request.session.flash(u'Logged in successfully.')
            return HTTPFound(location=came_from, headers=headers)

    request.session.flash(u'Failed to login.')
    return HTTPFound(location=came_from)


@view_config(permission='post', route_name='logout')
def logout_view(request):
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(location=request.route_url('main'), headers=headers)


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_longitudinal_longitudinal_longitudinal_register_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

