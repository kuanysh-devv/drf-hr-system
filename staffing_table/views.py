import io

from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from xlsxwriter import Workbook
import pandas as pd
from location.models import Location, Department
from location.serializers import DepartmentSerializer
from person.models import Person
from person.serializers import PersonSerializer
from position.models import PositionInfo
from position.serializers import PositionSerializer
from staffing_table.models import StaffingTable
from staffing_table.serializers import StaffingTableSerializer


class StaffingTableViewSet(viewsets.ModelViewSet):
    queryset = StaffingTable.objects.all()
    serializer_class = StaffingTableSerializer
    permission_classes = (IsAuthenticated,)


def downloadStaffingTable(request, *args, **kwargs):
    location_name = request.GET.get('locationName')
    staffing_data = None

    if location_name == 'ЦА':
        # Retrieve information for all free vacations (positions)
        staffing_data = StaffingTable.objects.filter(department__DepartmentName='ЦА')
    elif location_name == 'Весь Казахстан':
        # Retrieve information for each department separately
        staffing_data = StaffingTable.objects.exclude(department__DepartmentName='ЦА')

    df = pd.DataFrame.from_records(
        staffing_data.values('department__DepartmentName', 'position__positionTitle', 'current_count', 'max_count'))
    df['available_count'] = df['max_count'] - df['current_count']
    df = df.drop(['current_count', 'max_count'], axis=1)

    # Create a new workbook and add a worksheet
    output = io.BytesIO()
    workbook = Workbook(output)
    worksheet = workbook.add_worksheet()

    current_row = 0  # Initialize current_row to 0

    for department_data in staffing_data.values('department__DepartmentName').distinct():
        # Extract the department name
        department_name = department_data['department__DepartmentName']

        # Filter data for the current department
        department_df = pd.DataFrame.from_records(
            staffing_data.filter(
                department__DepartmentName=department_name
            ).values('position__positionTitle', 'current_count', 'max_count')
        )

        department_df['available_count'] = department_df['max_count'] - department_df['current_count']
        department_df = department_df.drop(['current_count', 'max_count'], axis=1)

        # Write the header for the department
        bold_format = workbook.add_format({'bold': True})
        worksheet.merge_range(current_row, 0, current_row, 1, department_name, bold_format)
        current_row += 1  # Increment current_row

        # Write the column headers with bold formatting
        headers = ['Должность', 'Доступно вакансий']
        for col_num, value in enumerate(headers):
            worksheet.write(current_row, col_num, value)

        current_row += 1  # Increment current_row for data

        # Write the data from the DataFrame
        for row_num, row_data in enumerate(department_df.itertuples(index=False), start=current_row):
            for col_num, value in enumerate(row_data):
                worksheet.write(row_num, col_num, value)

        # Increment current_row for the next department
        current_row += len(department_df)

        # Write the sum of 'Доступно вакансий' at the end of each department's data
        worksheet.merge_range(current_row, 0, current_row, 1, 'Итого', bold_format)
        worksheet.write_formula(current_row, 2, f'SUM(B{current_row - len(department_df) + 1}:B{current_row})')

        # Increment current_row for the next department's sum row
        current_row += 1

    overall_sum_row = current_row + 1
    bold_format = workbook.add_format({'bold': True})
    worksheet.merge_range(overall_sum_row, 0, current_row, 1, 'Итого по всем управлениям', bold_format)
    worksheet.write_formula(overall_sum_row, 2, f'SUM(C2:C{overall_sum_row - 1})')
    # Set the column widths based on the maximum content length
    for i, col in enumerate(df.columns, 1):
        max_len = max(df[col].astype(str).apply(len).max(), len(col))
        worksheet.set_column(i, i, max_len)

    # Save the Excel file
    workbook.close()

    # Create the HttpResponse with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=staffing_table.xlsx'
    output.seek(0)
    response.write(output.getvalue())
    return response


def getStaffingTable(request, *args, **kwargs):
    location_id = request.GET.get('location_id')

    try:
        location = Location.objects.get(pk=location_id)

        departments = Department.objects.filter(Location=location)
        data = {'Departments': []}
        for department in departments:
            DistinctPositionInfosToGetPositions = PositionInfo.objects.filter(department=department).distinct(
                'position')
            # GlavExpertDc
            # ExpertDC
            positionList = []
            for posinfo in DistinctPositionInfosToGetPositions:
                position_data = PositionSerializer(posinfo.position).data
                currentPositionInfos = PositionInfo.objects.filter(position=posinfo.position)
                personsOnPosition = Person.objects.filter(positionInfo__in=currentPositionInfos)
                position_data['persons'] = PersonSerializer(personsOnPosition, many=True).data

                staffing_table_entry = StaffingTable.objects.filter(
                    position=posinfo.position,
                    department=department
                ).first()

                if staffing_table_entry:
                    available_slots = staffing_table_entry.max_count - staffing_table_entry.current_count
                    position_data['available_slots'] = available_slots
                positionList.append(position_data)
            print(positionList)

            departamentSerialized = DepartmentSerializer(department).data
            departamentSerialized['positionList'] = positionList
            data['Departments'].append(departamentSerialized)

        return JsonResponse(data)

    except Location.DoesNotExist:
        return JsonResponse({'error': 'Location not found'}, status=404)
