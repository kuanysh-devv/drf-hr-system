# views.py
from django.forms import model_to_dict
from django.http import JsonResponse
from django.db.models import Q
from person.models import Person, FamilyComposition


# views.py
from django.http import JsonResponse
from django.db.models import Q
from person.models import Person

def filter_data(request):
    fields_param = request.GET.getlist("fields")

    filtered_persons = Person.objects.all()
    filter_conditions = Q()  # Initialize an empty Q object

    for field_param in fields_param:
        parts = field_param.split(':')
        if len(parts) == 3:
            model_name, field_name, value = parts
            field_lookup = f"{model_name.lower()}__{field_name}__exact"
            filter_condition = Q(**{field_lookup: value})
            filter_conditions &= filter_condition  # Add the condition to the Q object

    # Apply all conditions to the query
    filtered_persons = filtered_persons.filter(filter_conditions)

    # Convert the model objects to dictionaries
    result = [model_to_dict(p) for p in filtered_persons]

    return JsonResponse(result, safe=False)

