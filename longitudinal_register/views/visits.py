import json
import transaction

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

from pyramid_simpleform import Form

from longitudinal_register.models import Visit
from longitudinal_register import models

class VisitSchema(Schema):
    allow_extra_fields =  True
    form_id = validators.Int()
    #visit_type = validators.Int()
    health_id = validators.String()
    #provider = validators.Int()
    health_unit = validators.Int()
    visit_date = validators.DateValidator()
    #created_by = validators.Int()
    #created_date = validators.DateValidator()
    #modified_by = validators.Int()
    #modified_on = validators.DateValidator()
    
@view_config(route_name="visit_list", renderer="json")
def visit_list(request):
    DBSession.Query(Visit).all()

@view_config(route_name="visit_edit", renderer="patients/visit.html")
def visit_view(request):
    if not request.is_xhr:
        return {"Message": "Invalid request"}

    form = Form(request, schema=VisitSchema())
    if form.validate():
        visit = form.bind(Visit())
        with transaction.manager:
            DBSession.add(visit)


@view_config(route_name="visit_save", renderer="json")
def visit_save_view(request):
    health_id = request.matchdict['health_id']
    form_id = request.matchdict["form"]
    visit_date = request.POST["visit_date"]
    health_unit = request.POST["health_unit"]
    observations = []

    person = None
    with transaction.manager:
        person = models.DBSession.query(models.Person).\
            filter(models.Person.health_id == health_id).first()

    form = Form(request, schema=VisitSchema())
    if form.validate():
        for param,value in request.POST.iteritems():
            try:
                param =int(param)
                print param, value,'\n'
                with transaction.manager:
                    concept = models.DBSession.query(models.Concept).get(param)
                    if concept:
                        observation = models.Observation()
                        observation.concept = param
                        observation.concept_value
                        observations.append(observation)
            except ValueError:
                continue
        
        visit = form.bind(models.Visit())
        visit.person = person.id
        visit.observations = observations
        models.DBSession.add(visit)
        models.DBSession.flush()
        #with transaction.manager:
        #    visit.observations = observations
        #    models.DBSession.merge(visit)
    else:
        #print form.all_errors()
        print form.is_error(visit_date)
    print request.POST
    return HTTPFound(request.route_url("patients_list_page"))
   

def visit_render_form(request):
    pass
