import xlsxwriter
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from xlsxwriter import Workbook
import pandas as pd
from location.models import Location, Department
from location.serializers import LocationSerializer, DepartmentSerializer
from person.models import Person
from person.serializers import PersonSerializer
from position.models import Position, PositionInfo
from position.serializers import PositionSerializer, PositionInfoSerializer
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
        staffing_data = StaffingTable.objects.filter(department__DepartmentName='DC')
    elif location_name == 'Весь Казахстан':
        # Retrieve information for each department separately
        staffing_data = StaffingTable.objects.exclude(department__DepartmentName='DC')

    df = pd.DataFrame.from_records(
        staffing_data.values('department__DepartmentName', 'position__positionTitle', 'current_count', 'max_count'))
    df['available_count'] = df['max_count'] - df['current_count']
    df = df.drop(['current_count', 'max_count'], axis=1)
    print(df)
    # Create a new workbook and add a worksheet
    workbook = xlsxwriter.Workbook('staffing_table.xlsx')
    worksheet = workbook.add_worksheet()

    # Write the column headers with bold formatting
    bold_format = workbook.add_format({'bold': True})
    headers = ['Управление', 'Должность', 'Доступно вакансий']
    for col_num, value in enumerate(headers):
        worksheet.write(0, col_num, value, bold_format)

    # Write the data from the DataFrame
    for row_num, row_data in enumerate(df.itertuples(index=False), start=1):
        for col_num, value in enumerate(row_data):
            worksheet.write(row_num, col_num, value)

    # Set the column widths based on the maximum content length
    for i, col in enumerate(df.columns, 1):
        max_len = max(df[col].astype(str).apply(len).max(), len(col))
        worksheet.set_column(i, i, max_len)

    # Save the Excel file
    workbook.close()

    # Create the HttpResponse with the Excel file
    with open('staffing_table.xlsx', 'rb') as excel_file:
        response = HttpResponse(excel_file.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=staffing_table.xlsx'
        return response


def getStaffingTable(request, *args, **kwargs):
    location_id = request.GET.get('location_id')

    try:
        location = Location.objects.get(pk=location_id)

        departments = Department.objects.filter(Location=location)
        depSerializer = DepartmentSerializer(departments, many=True)
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
