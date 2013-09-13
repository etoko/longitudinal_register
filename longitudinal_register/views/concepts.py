import transaction

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import formencode

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from sqlalchemy.orm import joinedload

from longitudinal_register import models


headings = [[30, "Name"], [70, "Description"]]

class ConceptSchema(formencode.Schema):
    name = formencode.validators.String(not_empty=True)
    description = formencode.validators.String()
    allow_extra_fields = True


class ConceptAnswerSchema(formencode.Schema):
    concept = formencode.validators.Int()
    concept_answer = formencode.validators.Int()
    allow_extra_fields = True
    

class ConceptAnswersSchema(formencode.Schema):
     concept = formencode.validators.Int()
     concept_answer = formencode.ForEach(formencode.validators.Int())
     allow_extra_fields = True


@view_config(route_name="concept_save", renderer="json")
def concept_save_view(request):
    if "concept" in request.POST:
        form = Form(request, schema=ConceptAnswersSchema())
        if form.validate():
            answers = []
            concept_answers = form.bind(models.ConceptAnswer())
            concept = concept_answers.concept
            concept_answers = concept_answers.concept_answer

            for concept_answer in concept_answers:
                answer = models.ConceptAnswer()
                answer.concept = concept
                answer.concept_answer = concept_answer
                answers.append(answer)
           
            with transaction.manager:
                models.DBSession.add_all(answers)
        else:
            print form.all_errors()
            print "NOT VALIDATED"
        return "I saw it"

    form = Form(request, schema=ConceptSchema())
    concept_model = None
    if form.validate():
        concept = form.bind(models.Concept())
        #with transaction.manager:
        #    models.DBSession.add(concept)
        concept_model = models.DBSession.merge(concept)
        models.DBSession.flush()
        return HTTPFound(request.route_url("concept_edit_page", page="Concepts",\
            concept_id=concept_model.id))
    else:
        print "Failed"


@view_config(route_name="concept_add_page", renderer="concepts/add.html")
def concept_add_page(request):
    form = Form(request, schema=ConceptSchema)
    return {"page": "New Concept", "form": FormRenderer(form)}


@view_config(route_name="concept_edit_page", renderer="concepts/edit.html")
def concept_edit_page(request):
    concept_id = request.matchdict["concept_id"]
    form = Form(request, schema=ConceptSchema)
    concept = models.DBSession.query(models.Concept).get(concept_id)
    return {"page": "New Concept", "form": FormRenderer(form), \
           "concept": concept,"concepts": concepts()}


@view_config(route_name="concept_list_page", renderer="concepts/list.html")
def concept_list_page(request):
    concepts = models.DBSession.query(models.Concept).options(joinedload(models.Concept.concept_answers)).all()
    concepts = [(concept.id, concept.name) for concept in concepts]
    return {"page": "Concepts", "items":concepts, "headings": headings}


def concepts():
    concepts = models.DBSession.query(models.Concept).all()
    concepts = [(concept.id, concept.name) for concept in concepts]
    return concepts


####ConceptDataTypes####################
concept_headings = [[40, "Name"], [60, "Description"]]

class ConceptDataTypeSchema(formencode.Schema):
    name = formencode.validators.String(not_empty=True)
    description = formencode.validators.String()
    allow_extra_fields = True
    

@view_config(route_name="concept_datatype_list_page", renderer="concepts/datatype/list.html")
def concept_datatype_list_page(request):
    return list_page_dict

@view_config(route_name="concept_datatype_save_page", renderer="concepts/datatype/save.html")
def concept_datatype_save_page(request):
    form = Form(request, schema=ConceptDataTypeSchema)
    return {"page": "Concept Data Type", "form": FormRenderer(form)}

def concept_datatypes():
    with transaction.manager:
        return models.DBSession.query(models.ConceptDataType).all()
    return None


@view_config(route_name="concept_datatype_save", renderer="json")
def concept_datatype_save_view(request):
    print "Reached ME!!!"
    if "concept_datatype" in request.POST:
       form = Form(request, schema=ConceptDataTypeSchema)
       if form.validate():
           concept_datatype = form.bind(models.ConceptDataType())
           with transaction.manager:
               models.DBSession.merge(concept_datatype)
    return HTTPFound(request.route_url("concept_datatype_list_page", page= "Concept Data Type", headings= concept_headings, items= concept_datatypes()))


list_page_dict = {"page": "Concept Data Type", "headings": concept_headings, "items": concept_datatypes()}
concept_datatypes_save_page = {"page": "Concept Data Type"}
