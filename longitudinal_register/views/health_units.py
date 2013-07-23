import transaction
from pyramid.view import view_config
from pyramid import httpexceptions as exc

import formencode
from formencode import Schema

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from sqlalchemy.orm import (
    joinedload,
    joinedload_all,
    )

from longitudinal_register import models


health_unit_headings = [[40, "Name"], [30, "Type"], [30, "Location"]]

class HealthUnitSchema(Schema):
    name = formencode.validators.String(not_empty=True)
    location = formencode.validators.Int()
    health_unit_type_id = formencode.validators.Int()
    allow_extra_fields = True


@view_config(route_name="health_units_list", renderer="health_units/list.html")
def health_unit_list_page(request):
    health_units = models.DBSession.query(models.HealthUnit).\
        options(joinedload("health_unit_type" )).all()
    return {"page": "Health Units", "items": health_units, "headings": health_unit_headings}

@view_config(route_name="health_unit_save_page", renderer="health_units/edit.html")
def health_unit_save_page(request):
    form = Form(request, schema=HealthUnitSchema())
    locations = models.DBSession.query(models.Location).all()
    location_list = [[location.id, location.name] for location in locations]
    health_unit_types = models.DBSession.query(models.HealthUnitType).all()
    unit_types = \
        [(health_unit.id, health_unit.name) for health_unit in health_unit_types]
    print len(locations)
    print location_list
    return {"page": "Create New Health Unit", "form": FormRenderer(form), \
        "locations": location_list, "health_unit_types": unit_types}

@view_config(route_name="health_unit_save", renderer="json")
def health_unit_add(request):
    form = Form(request, schema=HealthUnitSchema())
    health_unit_id = None
    if form.validate():
        health_unit = form.bind(models.HealthUnit())
        h_unit = None
        with transaction.manager:
            #location = models.DBSession.query(models.Location).get(health_unit.location)
            #unit_type = models.DBSession.query(models.HealthUnitType).get(health_unit.health_unit_type_id)
            #health_unit.location = location
            #health_unit.health_unit_type_id = unit_type
            h_unit = models.DBSession.merge(health_unit)
            health_unit_id = h_unit.id
            print "HEALTH UNIT ID: ", health_unit_id
        health_units = models.DBSession.query(models.HealthUnit).all()
        units = [(health_unit.id, health_unit.name) for health_unit in health_units]
        return exc.HTTPFound(request.route_url("health_unit_dashboard", health_unit_id=health_unit_id,page="Health Units", items=units, headings=health_unit_headings))
    else:
        print form.all_errors()
        return "Failed"

@view_config(route_name="health_unit_dashboard", renderer="health_units/dashboard.html")
def health_unit_dashboard(request):
    print request.matchdict
    health_unit_id = request.matchdict["health_unit_id"]
    health_unit = models.DBSession.query(models.HealthUnit).get(health_unit_id)
    return {"page": health_unit.name + " Dashboard", "health_unit": health_unit}


###Health Unit Types

class HealthUnitTypeSchema(Schema):
    name = formencode.validators.String(not_empty=True)
    description = formencode.validators.String()
    allow_extra_fields = True
    
headings = [[40, "Name"], [60, "Description"]]
@view_config(route_name="health_unit_type_save_page", renderer="health_units/types/edit.html")
def health_unit_type_save_page(request):
    form = Form(request, schema=HealthUnitTypeSchema)
    return {"page": "Add Health Unit Type", "form": FormRenderer(form)}

@view_config(route_name="health_unit_type_save", renderer="json")
def health_unit_type_save_view(request):
    form = Form(request, schema=HealthUnitTypeSchema())
    if form.validate():
        health_unit_type = form.bind(models.HealthUnitType())
        with transaction.manager:
            models.DBSession.add(health_unit_type)
        return exc.HTTPFound(request.route_url("health_unit_type_list", \
            page="Health Unit Types", headings= headings))
    else:
        print "Validation Failed!!!!"
        print form.all_errors()

@view_config(route_name="health_unit_type_list", renderer="health_units/types/list.html")
def health_unit_type_list_page(request):
    health_unit_types = models.DBSession.query(models.HealthUnitType).all()
    return {"page": "Health Unit Types", "items": health_unit_types, "headings": headings}
    

#@view_config(route_name="health_unit_savepage", renderer="health_units/edit.html")
#def health_unit_save_page(request):
#    print "Reached ME!!"
#    return {"page": "New Health Unit", "form": renderers.FormRenderer(form)}
