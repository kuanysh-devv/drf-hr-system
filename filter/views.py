# views.py
from datetime import datetime

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
    filter_conditions = Q()

    for field_param in fields_param:
        parts = field_param.split(':')
        print("0")
        if len(parts) == 3:
            model_name, field_name, value = parts

            if "Date" in field_name or "date" in field_name:
                print("1")
                try:
                    start_date_str, end_date_str = value.split('_')
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if start_date == end_date:
                        # If the start_date and end_date are the same, it's an exact date match
                        field_lookup = f"{model_name.lower()}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                    else:
                        print("2")
                        # Otherwise, it's a date range filter
                        field_lookup = f"{model_name.lower()}__{field_name}__range"
                        filter_condition = Q(**{field_lookup: [start_date, end_date]})
                    filter_conditions &= filter_condition
                except ValueError:
                    continue  # Skip invalid date formats

            else:
                print("3")
                # For non-date fields, use an exact match
                field_lookup = f"{model_name.lower()}__{field_name}__exact"
                filter_condition = Q(**{field_lookup: value})
                filter_conditions &= filter_condition

    filtered_persons = filtered_persons.filter(filter_conditions)
    result = [model_to_dict(p) for p in filtered_persons]

    return JsonResponse(result, safe=False)
