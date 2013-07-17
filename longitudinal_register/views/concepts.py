
from pyramid.views import view_config

import formencode

from longitudinal_register import models

class ConceptSchema(formencode.Schema):
    name = formencode.validators.Text(not_empty=True)
    description = formencode.validators.Text()
    allow_extra_fields = True
    
class ConceptAnswerSchema(formencode.Schema):
    pass

@view_config(route_name="concept_add_view", renderer="json")
def concept_add_view(request):
    pass

@view_config(route_name="concept_add_page", renderer="concepts/edit.html")
def concept_add_page(request):
    pass

@view_config(route_name="concept_list_view", renderer="json")
def concept_list_view(request):
    pass

@view_config(route_name="concept_list_page", renderer="concepts/list.html")
def concept_list_page(request):
    pass
