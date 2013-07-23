import transaction

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import formencode

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from longitudinal_register import models

class ConceptSchema(formencode.Schema):
    name = formencode.validators.String(not_empty=True)
    description = formencode.validators.String()
    concept_answers = formencode.ForEach(formencode.validators.Int())
    allow_extra_fields = True
    
class ConceptAnswerSchema(formencode.Schema):
     concept = formencode.validators.Int()
     concept_answer = formencode.validators.Int()
     allow_extra_fields = True

headings = [[30, "Name"], [70, "Description"]]

@view_config(route_name="concept_add_view", renderer="json")
def concept_add_view(request):
    print request.params.mixed()

    form = Form(request, schema=ConceptSchema())
    if form.validate():
        concept = form.bind(models.Concept(), exclude="concept_answers")
        #with transaction.manager:
        #    models.DBSession.add(concept)
        models.DBSession.add(concept)
        models.DBSession.flush()
        #print concept.id
        concept_answers = request.params['concept_answers']
        answers = []
        if len(concept_answers):
            for concept_answer in concept_answers:
                c_answer = models.ConceptAnswer()
                c_answer.concept = concept.id
                c_answer.answer_concept = concept_answer
                answers.append(c_answer)
            with transaction.manager:
                models.DBSession.add_all(answers)

        concepts = models.DBSession.query(models.Concept).all()
        concepts = [(concept.id, concept.name) for concept in concepts]
    else:
        print "Failed"
    return HTTPFound(request.route_url("concept_list_page", page="Concepts",\
        headings=headings))

@view_config(route_name="concept_add_page", renderer="concepts/edit.html")
def concept_add_page(request):
    form = Form(request, schema=ConceptSchema)
    return {"page": "New Concept", "form": FormRenderer(form), "concepts": concepts()}

#@view_config(route_name="concept_list_view", renderer="json")
#def concept_list_view(request):
#    pass

@view_config(route_name="concept_list_page", renderer="concepts/list.html")
def concept_list_page(request):
    concepts = models.DBSession.query(models.Concept).all()
    concepts = [(concept.id, concept.name) for concept in concepts]
    return {"page": "Concepts", "items":concepts, "headings": headings}


def concepts():
    concepts = models.DBSession.query(models.Concept).all()
    concepts = [(concept.id, concept.name) for concept in concepts]
    return concepts
