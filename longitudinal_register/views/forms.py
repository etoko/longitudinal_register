
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

from longitudinal_register import models

headings = [[30, "Name"],[70, "Description"]]

class FormSchema(Schema):
    name = formencode.validators.String(not_empty=True)
    description = formencode.validators.String()
    allow_extra_fields = True

class FormConceptSchema(Schema):
    form = formencode.validators.Int()
    concepts = formencode.ForEach(formencode.validators.Int())
    allow_extra_fields = True

    
@view_config(route_name="form_list", renderer="forms/list.html")
def form_list_page(request):
    forms = models.DBSession.query(models.Form).all()
    return {"page": "List of forms", "items":forms, "headings":headings}

@view_config(route_name="form_add_page", renderer="forms/add.html")
def form_add_page(request):
    form = Form(request, schema=FormSchema())
    return {"page": "New Form", "form": FormRenderer(form)}

@view_config(route_name="form_edit_page", renderer="forms/edit.html")
def form_edit_page(request, **kwargs):
    form_id = request.matchdict["form_id"]
    form = Form(request, schema=FormSchema())
    form_model = models.DBSession.query(models.Form).options(joinedload('form_concepts')).get(form_id)
    concepts = form_model.form_concepts
    concepts = [models.DBSession.query(models.Concept).get(concept.concept) for concept in concepts]
    concepts = [(concept.id, concept.name) for concept in concepts]
    return {"page": "Modify Form", "form": FormRenderer(form), \
    "concepts": get_concepts(), "form_concepts":concepts, "form_model": form_model}

@view_config(route_name="form_save", renderer="json")
def form_save(request):
    form_id = request.params["form"]
    if form_id:
        form = Form(request, schema=FormConceptSchema())
        if form.validate():
            concepts = []
            form_concepts = form.bind(models.FormConcept())
            form_id = form_concepts.form
            form_concepts = form_concepts.concepts
 
            for form_concept in form_concepts:
                concept = models.FormConcept()
                concept.form = form_id
                concept.concept = form_concept
                concepts.append(concept)

            with transaction.manager:
                models.DBSession.add_all(concepts)

            return HTTPFound(request.route_url("form_list", page="List of Forms", \
                items=get_forms(), headings=headings))
        else:
            print "validation_failed"
            print form.all_errors()
            print request.params
            return

    form = Form(request, schema=FormSchema)
    if form.validate():
        form_model  = form.bind(models.Form())
        #with transaction.manager:
        #    models.DBSession.merge(form_model)
        form_model = models.DBSession.merge(form_model)
        models.DBSession.flush()
        print form_model.id
 
        return HTTPFound(request.route_url(\
           "form_edit_page", page="Forms", form_id=form_model.id,\
           form=FormRenderer(form)))
    else:
        print "validation Failed!!!"

@view_config(route_name="form_list_format", renderer="json")
def form_list(request):
    list_format = request.matchdict["format"]
    forms = get_forms() 
    forms = [(form.id, form.name) for form in forms]
    return {"aaData": forms}

def get_forms():
    return models.DBSession.query(models.Form).all()

def get_concepts():
    concepts = models.DBSession.query(models.Concept).all()
    return [(concept.id,concept.name) for concept in concepts]
    
