import json

from pyramid.httpexceptions import (
  exception_response,
  HTTPFound,
  HTTPNotFound,
  HTTPForbidden,
  )
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.static import static_view
from pyramid.security import authenticated_userid, forget, remember
from pyramid.view import view_config

from formencode import Schema
from formencode import validators

from longitudinal_register.models import Visit

class VisitSchema(Schema):
    id = validators.Int()
    visit_type = validators.Int()
    patient = validators.Int()
    provider = validators.Int()
    health_unit = validators.Int()
    visit_date = validators.DateValidator()
    created_by = validators.Int()
    created_date = validators.DateValidator()
    modified_by = validators.Int()
    modified_on = validators.DateValidator()
    
@view_config(route_name="visit_list", renderer="json")
def list_visits(request):
    DNSession.Query(Visit).all()

@view_config(route_name="visit_edit", renderer="patients/visit.html")
def visit_view(request):
    if not request.is_xhr:
        return {"Message": "Invalid request"}

    form = Form(request, schema=VisitSchema())
    if form.validate():
        visit = form.bind(Visit())
        with transaction.manager:
            DBSession.add(visit)
