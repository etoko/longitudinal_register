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

from formencode import Schema, validators
import formencode

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from sqlalchemy.orm import joinedload

from webhelpers.paginate import (
  Page,
  PageURL,
  )
import longitudinal_register

#from longitudinal_register.controllers import (
#  PatientController,
#  models.PersonController,
#  UserController,
#  )
from longitudinal_register import models

headings = [[20, "Health Id"], [40, "Name"], [20, "Location"]]

class PersonSchema(Schema):
    health_id = validators.String(not_empty=True)
    surname = validators.String(not_empty=True)
    other_names = validators.String(not_empty=True)
    gender = validators.String(not_empty=True)
    dob = validators.DateConverter(month_style='dd/mm/yyyy')
    location = validators.Int()
    allow_extra_fields  = True
    #filter_extra_fields=True
#    dob_estimated = validators.String()
    #status = validators.String()

@view_config(route_name="person_save_view", renderer="json")
def person_add_view(request):
    health_id = request.POST['health_id']
    form = Form(request, schema=PersonSchema())
    if form.validate():
        person = form.bind(models.Person())
        with transaction.manager:
            models.DBSession.add(person)
            
        return HTTPFound(request.route_url("patient_dashboard_page",\
           health_id=health_id, page= "Patient Dashboard"))
            #page= "Patients List", health_id= health_id)
    else:
        print "Form Validation Failed"
        print form.all_errors()
        print request.POST
        return {"message": "Reched ME!!"}

@view_config(route_name="patient_dashboard_page", renderer="patients/dashboard.html")
def patient_dashboard(request):
    health_id = request.matchdict["health_id"]
    person = models.DBSession.query(models.Person).\
        options(joinedload(models.Person.relations))\
        .filter(models.Person.health_id == health_id).first()
    if person is None:
        person = models.DBSession.query(models.Person).get(health_id)
    location = models.DBSession.query(models.Location).get(person.location)
    visits = []
    if person is not None:
        visits = models.DBSession.query(models.Visit)\
            .filter(models.Visit.person == person.id).all()
    forms = models.DBSession.query(models.Form).all()
    print forms
    return {"page": "Patient Dashboard", "person": person, "forms": forms, "location":location\
        , "visits": visits}


@view_config(route_name="patient_add_page", renderer="patients/edit.html")
def patients_add_page(request):
    form = Form(request, schema=PersonSchema)
    locations = models.DBSession.query(models.Location).all()
    locations = [(location.id, location.name) for location in locations]
    return {'form': FormRenderer(form), "page": "Add Patient", \
        "locations": locations}

@view_config(route_name="patients_list_page", renderer="patients/list.html")
def patients_list_page(request):
    patients = models.DBSession.query(models.Person).all()
    return {"page": "Patients List", "patients": patients, "items": patients, \
        "headings": headings}


#Relationships#######################################

class RelationshipSchema(Schema):
    person_a = formencode.validators.Int()
    person_b = formencode.validators.Int()
    type = formencode.validators.Int()
    allow_extra_fields = True

@view_config(route_name="person_relations_add_page", renderer="patients/relations.add.html")
def person_relation_add_page(request):
    return {"page": "Add New Relation"}

@view_config(route_name="person_relations_list", renderer="patients/relations/list.html")
def person_relations_page(request):
    form = Form(request, schema=ANCSchema)
    relationship_types = models.DBSession.query(models.RelationshipType).all()
    items = patients_list_page(request)
    items["form"] = FormRenderer(form)
    items["relationship_types"] = \
        [(relationship_type.id, relationship_type.name) for relationship_type in relationship_types]
    items['person_a'] = request.matchdict['person_a']
    items['health_id'] = request.matchdict['person_a']
    
    return items


@view_config(route_name="person_relations_save", renderer="json")
def person_relation_save_view(request):
    print request.params.mixed()
    person_a = request.params['person_a']
    person_b = request.params['person_b']
    form = Form(request, RelationshipSchema())
    if form.validate():
        relationship = form.bind(models.Relationship())
        with transaction.manager:
            models.DBSession.add(relationship)
        return HTTPFound(request.route_url("patient_dashboard_page", health_id=person_a))
    else:
        print form.all_errors()


##Visits#########################################################################

class ANCSchema(formencode.Schema):
    """
    ANC Form
    """
    allow_extra_fields = True
    person_id = formencode.validators.PlainText(not_empty=True)
    date = formencode.validators.DateConverter(month_style='dd/mm/yyyy')
    health_unit = formencode.validators.Int()
    gestation_age = formencode.validators.Int()
    regiment = formencode.validators.PlainText(not_empty=True)
    clinical_staging = formencode.validators.PlainText(not_empty=True)
    date_of_delivery = formencode.validators.DateConverter(month_style="dd/mm/yyyy")
    delivery_outcome = formencode.validators.PlainText(not_empty=True)


@view_config(route_name="visit_add", renderer="forms/form.html")
def view_visit_page(request):
    visit_type = request.matchdict["form"]
    health_id = request.matchdict["health_id"]
    person = None
    form_type = None
    health_units = None
    with transaction.manager:
        person = models.DBSession.query(models.Person)\
            .filter(models.Person.health_id == health_id).first()
        form_type = models.DBSession.query(models.Form).\
            options(joinedload('form_concepts')).get(visit_type)
        health_units = models.DBSession.query(models.HealthUnit).all()
    health_units = \
        [(health_unit.id, health_unit.name) for health_unit in health_units]

    visit_form = request.matchdict["form"] 
    form = Form(request, schema="ANCSchema")
    form_concepts = form_type.form_concepts
    control_labels = {}
    if form_concepts:
        for concept in form_concepts:
            concept_model = models.DBSession.query(models.Concept).get(concept.concept)
            control_labels[concept.concept] = concept_model.name

    return {"page": form_type.name, "person": person, "form": FormRenderer(form), \
        "visit_type": visit_type, "form_type": form_type, \
        "control_labels": control_labels,
        "health_units": health_units,
        "count":0}
    #if visit_form == "anc":
    #    return {"page": visit_form,"person": person}
    #elif visit_form == "eid":
    #    return {"page": "eid",}
    #else:
    #    return {"page": "Unknown Visit", "person": person}
