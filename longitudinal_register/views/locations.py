import transaction

from pyramid.view import view_config
from pyramid.renderers import render_to_response
import formencode
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from longitudinal_register import models



headings = [[20,"District"], [20,"County"], [20,"Sub County"], \
        [20,"Parish"], [20,"Village"]]

class LocationSchema(formencode.Schema):
    name = formencode.validators.String(not_empty=True)
    #parent = formencode.validators.Int(not_empty=False)
    location_type = formencode.validators.Int(not_empty=False)
    allow_extra_fields = True

class LocationTypeSchema(formencode.Schema):
    name = formencode.validators.String(not_empty=True)
    notes = formencode.validators.String(not_empty=False)
    allow_extra_fields = True

@view_config(route_name="location_add", renderer="locations/list.html")
def location_add(request):
    form = Form(request, schema=LocationSchema())
    if form.validate():
        location = form.bind(models.Location())
        with transaction.manager:
           models.DBSession.add(location)
        locations = models.DBSession.query(models.Location).all()
        locations_list = [(location.id, location.name)  for location in locations]
        return {"page": "Locations", "items": locations_list, "headings": headings}
    else:
       print form.all_errors()
       print form.errors_for('parent')
       print "Form validation failed"

@view_config(route_name="location_add_view", renderer="locations/edit.html")
def location_add_view(request):
    form = Form(request, schema=LocationSchema())
    location_types = models.DBSession.query(models.LocationType).all()
    l_types = []
    #_types = [l_types.append((location_type.id, location_type.name)) for location_type in location_types]
    print l_types
    [l_types.append((location_type.id, location_type.name)) \
        for location_type in location_types]
    
    #Consider returning a list of locations one level above the stated location type
    locations = models.DBSession.query(models.Location).all()
    parents = []
    [ parents.append((location.id, location.name)) \
        for location in locations]
    return {"page": "New Location", "form": FormRenderer(form), "location_types": l_types, "parents": parents}

@view_config(route_name="locations_list", renderer="locations/list.html")
def location_list_view(request):
    location_types = models.DBSession.query(models.LocationType).all()
    locations = models.DBSession.query(models.Location).all()
    #Top to bottom approach
    #Step1: From the location_types get to the district (highest in hierarchy)
    #Step2: Use district location_type id to return list of all districts
    #Step3: For each  get the parent parish,
    #Step4: For each parish get parent subcounty and so on
    #print ["%d %s" % (district.id, district.name) for district in locations]
    for location_type in location_types: # Check for district location_type
        if location_type.name == "District":
           districts = {}
           for district in locations: # Search for a District Location
               if district.location_type == location_type.id:
                   counties = {}
                   for county in locations: # Iterate for counties
                       if county.parent == district.id:
                           subcounties = {}
                           for subcounty in locations:
                               if subcounty.parent == county.id:
                                   parishes = {}
                                   for parish in locations:
                                       if parish.parent == subcounty.id:
                                           villages = []
                                           for village in locations:
                                               if village.parent == parish.id:
                                                   villages.append(village)
                                           parishes[parish.name] = villages
                                   subcounties[subcounty.name] = parishes
                           counties[county.name] = subcounties
                   districts[district.name] = counties
           break #Now that we have found the district location_type prevent further looping
    #print districts
    #print districts
    items = [(location.id, location.name)for location in locations]
    print items
    return {"page": "Locations", "items": items, "headings": headings}
