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
from person.serializers import PersonSerializer


def filter_data(request):

    filtered_persons = Person.objects.all()
    filter_conditions = Q()

    for key, value in request.GET.items():
        parts = key.split(':')
        if len(parts) == 2:
            model_name, field_name = parts

            if "Date" in field_name or "date" in field_name:
                try:
                    start_date_str, end_date_str = value.split('_')
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if start_date == end_date:
                        # If the start_date and end_date are the same, it's an exact date match
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                    else:
                        # Otherwise, it's a date range filter
                        field_lookup = f"{model_name}__{field_name}__range"
                        filter_condition = Q(**{field_lookup: [start_date, end_date]})
                    filter_conditions &= filter_condition
                except ValueError:

                    start_date_str = value
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    field_lookup = f"{model_name}__{field_name}__exact"
                    filter_condition = Q(**{field_lookup: start_date})
                    filter_conditions &= filter_condition
                    continue  # Skip invalid date formats

            else:
                # For non-date fields, use an exact match
                field_lookup = f"{model_name.lower()}__{field_name}__exact"
                filter_condition = Q(**{field_lookup: value})
                filter_conditions &= filter_condition

        elif len(parts) == 1:
            field_name = parts[0]

            if "Date" in field_name or "date" in field_name:
                try:
                    start_date_str, end_date_str = value.split('_')
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if start_date == end_date:
                        # If the start_date and end_date are the same, it's an exact date match
                        field_lookup = f"{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                    else:
                        # Otherwise, it's a date range filter
                        field_lookup = f"{field_name}__range"
                        filter_condition = Q(**{field_lookup: [start_date, end_date]})
                    filter_conditions &= filter_condition
                except ValueError:

                    start_date_str = value
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    field_lookup = f"{field_name}__exact"
                    filter_condition = Q(**{field_lookup: start_date})
                    filter_conditions &= filter_condition
                    continue  # Skip invalid date formats

            else:
                # For non-date fields, use an exact match
                field_lookup = f"{field_name}__exact"
                filter_condition = Q(**{field_lookup: value})
                filter_conditions &= filter_condition

    filtered_persons = filtered_persons.filter(filter_conditions)
    result = [PersonSerializer(instance=p).data for p in filtered_persons]

    return JsonResponse(result, safe=False)
