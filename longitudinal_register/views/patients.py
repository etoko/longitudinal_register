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

from webhelpers.paginate import (
  Page,
  PageURL,
  )

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
    print "PROCESSING PATIENT.............................."
    if "health_id" in request.POST:
        
        print "TRUE"
    else:
        print "FALSE"
    #print "health_id" in request.params.mixed().keys()
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
        return {"message": "Reched ME!!"}

@view_config(route_name="patient_dashboard_page", renderer="patients/dashboard.html")
def patient_dashboard(request):
    health_id = request.matchdict["health_id"]
    person = models.DBSession.query(models.Person)\
        .filter(models.Person.health_id == health_id).first()
    location = models.DBSession.query(models.Location).get(person.location)
    patient = models.DBSession.query(models.Patient)\
        .filter(models.Patient.person == person.id).first()
    visits = []
    if patient is not None:
        visits = models.DBSession.query(models.Visit)\
            .filter(models.Visit.patient == patient.id).all()
    return {"page": "Patient Dashboard", "person": person, "location":location\
        , "visits": visits}
#
#@view_config(route_name="add_person", renderer="persons/edit.html")
#def page_add_person_(request):
#    return {"person": "edit"}
#
#@view_config(route_name="list_persons", renderer="persons/list.html")
#def page_list_persons(request):
#    return {"persons": "Us", "other": "The others"}
#
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
    #patients = [(patient.health_id, patient.surname + " " + patient.other_names)\
    #    for patient in patients]
    return {"page": "Patients List", "patients": patients, "items": patients, \
        "headings": headings}


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
    person = models.DBSession.query(models.Person)\
        .filter(models.Person.health_id == health_id).first()
    visit_form = request.matchdict["form"] 
    form = Form(request, schema="ANCSchema")
    return {"page": visit_form,"person": person, "form": FormRenderer(form), \
        "visit_type": visit_type}
    #if visit_form == "anc":
    #    return {"page": visit_form,"person": person}
    #elif visit_form == "eid":
    #    return {"page": "eid",}
    #else:
    #    return {"page": "Unknown Visit", "person": person}
