
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

class FormSchema(Schema):
    name = formencode.validators.String(not_empty=True)
    description = formencode.validators.String()
    allow_extra_fields = True
    

@view_config(route_name="form_save_page", renderer="forms/add.html")
def form_add_page(request):
    form = Form(request, schema=FormSchema())
    return {"page": "New Form", "form": FormRenderer(form)}

@view_config(route_name="form_edit_page", renderer="forms/edit.html")
def form_edit_page(request):
    form = Form(request, schema=FormSchema())
    return {"page": "New Form", "form": FormRenderer(form)}
