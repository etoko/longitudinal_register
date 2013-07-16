import transaction
from pyramid.view import view_config

import formencode
from formencode import Schema

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from longitudinal_register import models


headings = [[40, "Name"], [30, "Type"], [30, "Location"]]

@view_config(route_name="health_units_list", renderer="health_units/list.html")
def health_unit_list_page(request):
    units = models.DBSession.query(models.HealthUnit).all()
    health_units = [(unit.id, unit.name) for unit in units]
    return {"page": "Health Units", "items": health_units, "headings": headings}

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

class HealthUnitSchema(Schema):
    name = formencode.validators.String(not_empty=True)
    location = formencode.validators.Int()
    health_unit_type = formencode.validators.Int()
    allow_extra_fields = True

@view_config(route_name="health_unit_save", renderer="health_units/list.html")
def health_unit_add(request):
    form = Form(request, schema=HealthUnitSchema())
    if form.validate():
        health_unit = form.bind(models.HealthUnit())
        with transaction.manager:
            models.DBSession.add(health_unit)
        health_units = models.DBSession.query(models.HealthUnit).all()
        units = [(health_unit.id, health_unit.name) for health_unit in health_units]
        return {"page": "Health Units", "items": units, "headings": headings}
    else:
        print form.all_errors()
        return "Failed"

#@view_config(route_name="health_unit_savepage", renderer="health_units/edit.html")
#def health_unit_save_page(request):
#    print "Reached ME!!"
#    return {"page": "New Health Unit", "form": renderers.FormRenderer(form)}
