import base64
import io
import json
from datetime import datetime, timedelta
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.shared import Inches
from docx.shared import Pt

from birth_info.models import BirthInfo
from decree.models import DecreeList, TransferInfo, RankUpInfo, AppointmentInfo
from education.models import Education, AcademicDegree
from education.serializers import EducationSerializer, AcademicDegreeSerializer
from location.models import Department
from military_rank.models import RankInfo, MilitaryRank
from person.models import Person
from photo.models import Photo
from position.models import Position, PositionInfo
from working_history.models import WorkingHistory
from military_rank.tasks import create_rank_info_after_months


@csrf_exempt
def generate_work_reference(request, person_id):
    # Fetch the necessary data
    person = get_object_or_404(Person, pk=person_id)
    birth_info = BirthInfo.objects.get(personId=person)
    birth_date = str(birth_info.birth_date)
    birth_date_format = datetime.strptime(birth_date, '%Y-%m-%d')
    formatted_date = birth_date_format.strftime('%d.%m.%Y')

    rankInfo = RankInfo.objects.get(person=person)

    education_objects = Education.objects.filter(personId=person.id)
    education_data = EducationSerializer(education_objects, many=True).data

    if len(education_data) != 0:
        first_education = education_data[0]
        date_edu_string = first_education['educationDateOut']  # Assuming 'first_education' is an OrderedDict
        date_obj = datetime.strptime(date_edu_string, '%Y-%m-%d')

    academic_degrees_objects = AcademicDegree.objects.filter(personId=person.id)
    academic_degrees_data = AcademicDegreeSerializer(academic_degrees_objects, many=True).data
    if len(academic_degrees_data) != 0:
        first_academic_degree = academic_degrees_data[0]
        date_academ_string = first_academic_degree['academicDiplomaDate']
        date_academ_obj = datetime.strptime(date_academ_string, '%Y-%m-%d')

    persons_photo = Photo.objects.get(personId=person)
    photo_base64 = persons_photo.photoBinary

    # Replace with your photo field
    photo_binary = base64.b64decode(photo_base64)
    image = io.BytesIO(photo_binary)

    def calculate_experience(working_histories, type):
        total_experience = timedelta()

        if type == 'All':
            for working_history in working_histories:
                start_date = working_history.startDate
                end_date = working_history.endDate or datetime.now().date()
                experience = end_date - start_date
                total_experience += experience

        if type == 'PravoOhranka':
            for working_history in working_histories:
                if working_history.isPravoOhranka:
                    start_date = working_history.startDate
                    end_date = working_history.endDate or datetime.now().date()
                    experience = end_date - start_date
                    if working_history.HaveCoefficient:
                        experience = experience * 1.5
                    total_experience += experience

        total_years = total_experience.days // 365
        remaining_days = total_experience.days % 365
        total_months = remaining_days // 30
        remaining_days %= 30

        overall_experience = {
            'years': total_years,
            'months': total_months,
            'days': remaining_days
        }

        return overall_experience

    # Load the Word document template
    template_path = 'docx_generator/static/templates/spravka_template.docx'  # Update with the path to your template
    document = Document(template_path)
    tables = document.tables
    p2 = tables[0].rows[0].cells[2].add_paragraph()
    r2 = p2.add_run()
    r2.add_picture(image, width=Inches(1.2))

    # Define a function to replace placeholders in the document
    def replace_placeholder(placeholder, replacement):
        for paragraph1 in tables[0].rows[0].cells[0].paragraphs:
            if placeholder in paragraph1.text:
                for run1 in paragraph1.runs:
                    if placeholder in run1.text:
                        run1.text = run1.text.replace(placeholder, replacement)
                        run1.font.size = Pt(12)  # Adjust the font size if needed

    # Replace placeholders with actual data
    replace_placeholder('placeholder', f"{person.firstName}")
    replace_placeholder('surname', f"{person.surname}")
    replace_placeholder('patronymic', f"{person.patronymic}")
    replace_placeholder('nationality', f"{person.nationality}")
    replace_placeholder('position', person.positionInfo.position.positionTitle)
    replace_placeholder('iin', person.iin)
    replace_placeholder('birth_date', str(formatted_date))
    replace_placeholder('region', birth_info.region)
    replace_placeholder('city', birth_info.city)
    replace_placeholder('rank', rankInfo.militaryRank.rankTitle)

    if len(education_data) == 0:
        replace_placeholder('education', "Не имеет")
    else:
        replace_placeholder('education',
                            f"окончил(а) {first_education['educationPlace']} в {date_obj.year} году на специальность {first_education['speciality']}")
    # Create a BytesIO object to save the modified document

    if len(academic_degrees_data) == 0:
        replace_placeholder('academicdegree', "Не имеет")
    else:
        replace_placeholder('academicdegree',
                            f"получил(а) {first_academic_degree['academicDegree']} в {first_academic_degree['academicPlace']} в {date_academ_obj.year} году")
    # Create a BytesIO object to save the modified document

    work_history = WorkingHistory.objects.filter(personId=person).order_by('startDate')
    education_history = Education.objects.filter(personId=person).order_by('educationDateIn')

    pravo_experience = calculate_experience(working_histories=work_history,
                                            type='PravoOhranka')

    if pravo_experience['years'] == 1:
        yearString = 'год'
    elif pravo_experience['years'] in [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54]:
        yearString = 'года'
    else:
        yearString = 'лет'

    if pravo_experience['months'] == 1:
        monthString = 'месяц'
    elif pravo_experience['months'] in [2, 3, 4]:
        monthString = 'месяца'
    else:
        monthString = 'месяцев'

    if pravo_experience['days'] == 1:
        dayString = 'день'
    elif pravo_experience['days'] in [2, 3, 4]:
        dayString = 'дня'
    else:
        dayString = 'дней'

    if pravo_experience['years'] == 0 and pravo_experience['months'] == 0:
        pravo_experience_string = str(pravo_experience['days']) + ' ' + dayString
    elif pravo_experience['years'] == 0:
        pravo_experience_string = (str(pravo_experience['months']) + ' ' + monthString + ' '
                                   + str(pravo_experience['days']) + ' ' + dayString)
    else:
        pravo_experience_string = str(pravo_experience['years']) + ' ' + yearString + ' ' + str(
            pravo_experience['months']) + ' ' + monthString + ' ' + str(pravo_experience['days']) + ' ' + dayString

    replace_placeholder('pravoexp', pravo_experience_string)

    # Create a new section in the document after a specific keyword
    keyword = "ДЕЯТЕЛЬНОСТЬ"  # Replace with the keyword you want to use
    for paragraph in document.paragraphs:
        if keyword in paragraph.text:
            section = paragraph._element
            break

    # Create a table with 2 columns for work history and education
    num_columns = 2
    table = document.add_table(rows=1, cols=num_columns)
    table.style = 'Table Grid'
    table.autofit = False
    table.allow_autofit = False

    # Define the column widths (adjust these as needed)
    table.columns[0].width = Inches(2)  # Date in and Date out
    table.columns[1].width = Inches(3)  # Place of education and work

    # Add a header row to the table
    table.rows[0].cells[0].text = "Дата"
    table.rows[0].cells[1].text = "Место деятельности и специальность"

    # Iterate through all the cells in the header row
    for cell in table.rows[0].cells:
        cell.paragraphs[0].paragraph_format.alignment = WD_ALIGN_VERTICAL.CENTER

        # Adjust the paragraph spacing to add padding (adjust the values as needed)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_before = Pt(6)  # Add space before text
        paragraph.paragraph_format.space_after = Pt(6)

        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
                run.bold = True
                # Iterate through all the cells in the table to add borders

    for entry in education_history:
        date_in = entry.educationDateIn.strftime('%d.%m.%Y')
        date_out = entry.educationDateOut.strftime('%d.%m.%Y')
        place = f"{entry.educationPlace}, Speciality: {entry.speciality}"
        table.add_row().cells[0].text = f"{date_in} - {date_out}"
        table.rows[-1].cells[1].text = place

    # Populate the table with work history and education data
    for entry in work_history:
        date_in = entry.startDate.strftime('%d.%m.%Y')
        date_out = None
        if entry.endDate:
            date_out = entry.endDate.strftime('%d.%m.%Y')
        place = f"{entry.organizationName}, должность: {entry.positionName}"
        if date_out is None:
            table.add_row().cells[0].text = f"{date_in} - по настоящее время"
            table.rows[-1].cells[1].text = place
        else:
            table.add_row().cells[0].text = f"{date_in} - {date_out}"
            table.rows[-1].cells[1].text = place

    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_before = Pt(6)  # Add space before text
                paragraph.paragraph_format.space_after = Pt(6)

    doc_stream = BytesIO()
    document.save(doc_stream)
    doc_stream.seek(0)

    # Prepare the HTTP response with the modified document
    response = HttpResponse(doc_stream.read(),
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename=work_reference.docx'

    return response


@csrf_exempt
def generate_appointment_decree(request):
    if request.method == 'POST':
        try:
            # Get the raw request body
            body = request.body.decode('utf-8')

            # Parse the JSON data from the request body
            data = json.loads(body)

            # Extract variables from the parsed data
            personId = data.get('personId')
            month_count = data.get('monthCount')
            base = data.get('base')
            appointmentType = data.get('appointmentType')
            decreeDate = data.get('decreeDate')

            # Get model instances
            personInstance = Person.objects.get(pk=personId)
            departmentInstance = personInstance.positionInfo.department
            positionInstance = personInstance.positionInfo.position
            positionTitle = positionInstance.positionTitle
            departmentName = departmentInstance.DepartmentName
            # Create required model instances...
            if not DecreeList.objects.filter(personId=personInstance, decreeType="Назначение",
                                             isConfirmed=False).first():
                decree_list_instance = DecreeList.objects.create(
                    decreeType="Назначение",
                    decreeDate=datetime.strptime(decreeDate, '%Y-%m-%d').date(),
                    personId=personInstance
                )
                if appointmentType == 'Впервые принятый':
                    AppointmentInfo.objects.create(
                        appointmentDepartment=departmentInstance,
                        appointmentPosition=positionInstance,
                        appointmentProbation=int(month_count),
                        appointmentBase=base,
                        appointmentType=appointmentType,
                        decreeId=decree_list_instance
                    )
                if appointmentType == 'Вновь принятый':
                    AppointmentInfo.objects.create(
                        appointmentDepartment=departmentInstance,
                        appointmentPosition=positionInstance,
                        appointmentProbation=None,
                        appointmentBase=base,
                        appointmentType=appointmentType,
                        decreeId=decree_list_instance
                    )

                if appointmentType == 'Впервые принятый':
                    three_months_later = datetime.strptime(decreeDate, '%Y-%m-%d').date() + timedelta(days=int(month_count) * 30 + 1)
                    if personInstance.rankInfo is None:
                        task = create_rank_info_after_months.apply_async(
                            args=(int(month_count), decree_list_instance.decreeNumber), eta=three_months_later)
                    else:
                        return JsonResponse(
                            {'error': 'Сотрудник уже имеет звание'}, status=400)

            else:
                return JsonResponse({'error': 'У сотрудника уже имеется приказ о назначении который не согласован'}, status=400)

            # Для склонения
            soglasnie = ['б', 'в', 'г', 'д', 'ж', 'з', 'й', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч',
                         'ш', 'щ']
            glasnie = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я']

            changedSurname = personInstance.surname
            changedFirstName = personInstance.firstName

            if personInstance.gender.genderName == 'Мужской':
                if personInstance.firstName[-1] in soglasnie:
                    changedFirstName = personInstance.firstName + 'а'
                else:
                    changedFirstName = personInstance.firstName

                if personInstance.surname[-2:] == 'ев' or personInstance.surname[-2:] == 'ов':
                    changedSurname = personInstance.surname + 'а'
                else:
                    changedSurname = personInstance.surname

            if personInstance.gender.genderName == 'Женский':
                if personInstance.firstName[-1] == 'а' and personInstance.firstName[-2] in soglasnie:
                    changedFirstName = personInstance.firstName[:-1]
                    changedFirstName = changedFirstName + 'у'
                else:
                    changedFirstName = personInstance.firstName

                if personInstance.surname[-3:] == 'ева' or personInstance.surname[-3:] == 'ова':
                    changedSurname = personInstance.surname[:-1]
                    changedSurname = changedSurname + 'у'
                else:
                    changedSurname = personInstance.surname

            personsFIO = changedSurname + ' ' + changedFirstName + ' ' + personInstance.patronymic
            personsFIOKaz = personInstance.firstName + ' ' + personInstance.patronymic + ' ' + personInstance.surname
            changedPositionTitle = positionTitle

            if positionTitle == 'Руководитель департамента':
                changedPositionTitle = 'Руководителя департамента'
            if positionTitle == 'Заместитель руководителя департамента':
                changedPositionTitle = 'Заместителя руководителя департамента'
            if positionTitle == 'Руководитель управления':
                changedPositionTitle = 'Руководителя управления'
            if positionTitle == 'Заместитель руководителя управления':
                changedPositionTitle = 'Заместителя руководителя управления'
            if positionTitle == 'Оперуполномоченный по особо важным делам':
                changedPositionTitle = 'Оперуполномоченного по особо важным делам'
            if positionTitle == 'Старший оперуполномоченный':
                changedPositionTitle = 'Старшего оперуполномоченного'
            if positionTitle == 'Оперуполномоченный':
                changedPositionTitle = 'Оперуполномоченного'

            changedDepartmentName = departmentName
            words = departmentName.split()
            if words[0] == 'Управление':
                words[0] = 'Управления'
                changedDepartmentName = ' '.join(words)
            if departmentName == 'ЦА':
                changedDepartmentName = 'Управления'
            if departmentName == 'ЦА':
                departmentName = 'Управление'
            baseKaz = None
            if base == 'представление':
                baseKaz = 'ұсыныс'
            if base == 'рапорт':
                baseKaz = 'баянат'
            if base == 'заявление':
                baseKaz = 'өтініш'
            if base == 'протокол и докладная записка':
                baseKaz = 'хаттама'

            # Load the Word document template
            if appointmentType == 'Впервые принятый':
                template_path = 'docx_generator/static/templates/appointment_template.docx'  # Update with the path to your template
                document = Document(template_path)
            if appointmentType == 'Вновь принятый':
                template_path = 'docx_generator/static/templates/appointment_template_secondly.docx'  # Update with the path to your template
                document = Document(template_path)

            # Define a function to replace placeholders in the document
            def replace_placeholder(placeholder, replacement):
                for paragraph1 in document.paragraphs:
                    if placeholder in paragraph1.text:

                        for run1 in paragraph1.runs:
                            if placeholder in run1.text:
                                run1.text = run1.text.replace(placeholder, replacement)
                                run1.font.size = Pt(14)  # Adjust the font size if needed
                                run1.font.name = 'Times New Roman'

            # Replace placeholders with actual data
            replace_placeholder('departmentName', f"{departmentName}")
            replace_placeholder('PersonsFio', f"{personsFIO}")
            replace_placeholder('PositionTitle', f"{changedPositionTitle}")
            replace_placeholder('ChangedDepartmentName', f"{changedDepartmentName}")
            replace_placeholder('monthCount', str(month_count))
            replace_placeholder('base', base)

            replace_placeholder('DepartmentNameKaz', f"{departmentInstance.DepartmentNameKaz}")
            replace_placeholder('PersonFioKaz', f"{personsFIOKaz}")
            replace_placeholder('positionTitleKaz', f"{positionInstance.positionTitleKaz}")
            replace_placeholder('variable4', baseKaz)
            doc_stream = BytesIO()
            document.save(doc_stream)
            doc_stream.seek(0)

            # Prepare the HTTP response with the modified document
            response = HttpResponse(doc_stream.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml'
                                                 '.document')
            response['Content-Disposition'] = f'attachment; filename=Приказ о назначении.docx'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неправильные JSON данные'}, status=400)

    return JsonResponse({'error': 'Неправильный метод запроса'}, status=405)


@csrf_exempt
def generate_transfer_decree(request):
    if request.method == 'POST':
        try:
            # Get the raw request body
            body = request.body.decode('utf-8')

            # Parse the JSON data from the request body
            data = json.loads(body)

            # Extract variables from the parsed data
            person_id = data.get('personId')
            newPositionTitle = data.get('newPosition')
            newDepartmentName = data.get('newDepartment')
            decreeDate = data.get('decreeDate')
            base = data.get('base')

            personInstance = Person.objects.get(pk=person_id)
            newDepartmentInstance = Department.objects.get(DepartmentName=newDepartmentName)
            newPositionInstance = Position.objects.get(positionTitle=newPositionTitle)

            currentPosition = PositionInfo.objects.get(person=personInstance).position
            currentDepartment = PositionInfo.objects.get(person=personInstance).department

            if not DecreeList.objects.filter(personId=personInstance, decreeType="Перемещение",
                                             isConfirmed=False).first():

                decree_list_instance = DecreeList.objects.create(
                    decreeType="Перемещение",
                    decreeDate=datetime.strptime(decreeDate, '%Y-%m-%d').date(),
                    personId=personInstance
                )

                TransferInfo.objects.create(
                    previousDepartment=currentDepartment,
                    previousPosition=currentPosition,
                    newDepartment=newDepartmentInstance,
                    newPosition=newPositionInstance,
                    transferBase=base,
                    decreeId=decree_list_instance
                )
            else:
                return JsonResponse({'error': 'У сотрудника уже имеется приказ о перемещении который не согласован'}, status=400)
            soglasnie = ['б', 'в', 'г', 'д', 'ж', 'з', 'й', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч',
                         'ш', 'щ']
            glasnie = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я']

            changedSurname = None
            changedFirstName = None

            if personInstance.gender.genderName == 'Мужской':
                if personInstance.firstName[-1] in soglasnie:
                    changedFirstName = personInstance.firstName + 'а'  # Қасымбаева Қуаныша Ахатұлы
                else:
                    changedFirstName = personInstance.firstName

                if personInstance.surname[-2:] == 'ев' or personInstance.surname[-2:] == 'ов':
                    changedSurname = personInstance.surname + 'а'  # Қасымбаева Қуаныша Ахатұлы
                else:
                    changedSurname = personInstance.surname

            if personInstance.gender.genderName == 'Женский':
                if personInstance.firstName[-1] == 'а' and personInstance.firstName[-2] in soglasnie:
                    changedFirstName = personInstance.firstName[:-1]
                    changedFirstName = changedFirstName + 'у'
                else:
                    changedFirstName = personInstance.firstName

                if personInstance.surname[-3:] == 'ева' or personInstance.surname[-3:] == 'ова':
                    changedSurname = personInstance.surname[:-1]
                    changedSurname = changedSurname + 'у'
                else:
                    changedSurname = personInstance.surname

            personsFIO = changedSurname + ' ' + changedFirstName + ' ' + personInstance.patronymic
            personsFIOKaz = personInstance.firstName + ' ' + personInstance.patronymic + ' ' + personInstance.surname

            changedPositionTitle = newPositionInstance.positionTitle
            changedCurrentPositionTitle = currentPosition.positionTitle

            if newPositionTitle == 'Руководитель департамента':
                changedPositionTitle = 'Руководителя департамента'
            if newPositionTitle == 'Заместитель руководителя департамента':
                changedPositionTitle = 'Заместителя руководителя департамента'
            if newPositionTitle == 'Руководитель управления':
                changedPositionTitle = 'Руководителя управления'
            if newPositionTitle == 'Заместитель руководителя управления':
                changedPositionTitle = 'Заместителя руководителя управления'
            if newPositionTitle == 'Оперуполномоченный по особо важным делам':
                changedPositionTitle = 'Оперуполномоченного по особо важным делам'
            if newPositionTitle == 'Старший оперуполномоченный':
                changedPositionTitle = 'Старшего оперуполномоченного'
            if newPositionTitle == 'Оперуполномоченный':
                changedPositionTitle = 'Оперуполномоченного'

            if currentPosition.positionTitle == 'Руководитель департамента':
                changedCurrentPositionTitle = 'Руководителя департамента'
            if currentPosition.positionTitle == 'Заместитель руководителя департамента':
                changedCurrentPositionTitle = 'Заместителя руководителя департамента'
            if currentPosition.positionTitle == 'Руководитель управления':
                changedCurrentPositionTitle = 'Руководителя управления'
            if currentPosition.positionTitle == 'Заместитель руководителя управления':
                changedCurrentPositionTitle = 'Заместителя руководителя управления'
            if currentPosition.positionTitle == 'Оперуполномоченный по особо важным делам':
                changedCurrentPositionTitle = 'Оперуполномоченного по особо важным делам'
            if currentPosition.positionTitle == 'Старший оперуполномоченный':
                changedCurrentPositionTitle = 'Старшего оперуполномоченного'
            if currentPosition.positionTitle == 'Оперуполномоченный':
                changedCurrentPositionTitle = 'Оперуполномоченного'

            changedDepartmentName = newDepartmentInstance.DepartmentName
            changedCurrentDepartmentName = currentDepartment.DepartmentName
            changedCurrentDepartmentNameKaz = currentDepartment.DepartmentNameKaz
            changedNewDepartmentNameKaz = newDepartmentInstance.DepartmentNameKaz

            words = newDepartmentName.split()
            if words[0] == 'Управление':
                words[0] = 'Управления'
                changedDepartmentName = ' '.join(words)
            if newDepartmentName == 'ЦА':
                changedDepartmentName = 'Управления'
            if newDepartmentName == 'ЦА':
                departmentName = 'Управление'

            words = currentDepartment.DepartmentName.split()
            if words[0] == 'Управление':
                words[0] = 'Управления'
                changedCurrentDepartmentName = ' '.join(words)
            if currentDepartment.DepartmentName == 'ЦА':
                changedCurrentDepartmentName = 'Управления'
            if currentDepartment.DepartmentName == 'ЦА':
                currentDepartment.DepartmentName = 'Управление'

            if currentDepartment.DepartmentNameKaz == 'Басқарма':
                changedCurrentDepartmentNameKaz = 'Басқармасының'
            else:
                changedCurrentDepartmentNameKaz = currentDepartment.DepartmentNameKaz + 'ның'

            if newDepartmentInstance.DepartmentNameKaz == 'Басқарма':
                changedNewDepartmentNameKaz = 'Басқармасының'
            else:
                changedNewDepartmentNameKaz = newDepartmentInstance.DepartmentNameKaz + 'ның'

            baseKaz = None
            if base == 'представление':
                baseKaz = 'ұсыныс'
            if base == 'рапорт':
                baseKaz = 'баянат'

            # Load the Word document template
            template_path = 'docx_generator/static/templates/transfer_template.docx'  # Update with the path to your template
            document = Document(template_path)

            # Define a function to replace placeholders in the document
            def replace_placeholder(placeholder, replacement):
                for paragraph1 in document.paragraphs:
                    if placeholder in paragraph1.text:

                        for run1 in paragraph1.runs:
                            if placeholder in run1.text:
                                run1.text = run1.text.replace(placeholder, replacement)
                                run1.font.size = Pt(14)  # Adjust the font size if needed
                                run1.font.name = 'Times New Roman'

            # Replace placeholders with actual data
            replace_placeholder('FIO', f"{personsFIO}")
            replace_placeholder('POSITIONTITLE', f"{changedPositionTitle}")
            replace_placeholder('DEPARTMENTNAME', f"{changedDepartmentName}")
            replace_placeholder('CURRENTP', f"{changedCurrentPositionTitle}")
            replace_placeholder('CURRENTD', f"{changedCurrentDepartmentName}")
            replace_placeholder('BASE', base)

            replace_placeholder('fio', f"{personsFIOKaz}")
            replace_placeholder('currentd', f"{changedCurrentDepartmentNameKaz}")
            replace_placeholder('currentp', f"{currentPosition.positionTitleKaz}")
            replace_placeholder('departmentname', f"{changedNewDepartmentNameKaz}")
            replace_placeholder('positiontitle', f"{newPositionInstance.positionTitleKaz}")
            replace_placeholder('base', baseKaz)

            doc_stream = BytesIO()
            document.save(doc_stream)
            doc_stream.seek(0)

            # Prepare the HTTP response with the modified document
            response = HttpResponse(doc_stream.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml'
                                                 '.document')
            response['Content-Disposition'] = f'attachment; filename=Приказ о перемещении.docx'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def generate_rankup_decree(request):
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            # Extract variables from the parsed data
            person_id = data.get('personId')
            newRankTitle = data.get('newRank')
            rankUpDate = data.get('rankUpDate')
            receivedType = data.get('receivedType')

            personInstance = Person.objects.get(pk=person_id)

            currentPosition = PositionInfo.objects.get(person=personInstance).position
            currentDepartment = PositionInfo.objects.get(person=personInstance).department

            personsRankInfo = RankInfo.objects.get(person=personInstance)
            personsPositionInfo = PositionInfo.objects.get(person=personInstance)

            try:
                newRankInstance = MilitaryRank.objects.get(rankTitle=newRankTitle)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Неправильное звание'}, status=400)

            newRankTitle = newRankInstance.rankTitle.lower()

            if personsRankInfo.militaryRank.order > newRankInstance.order:
                return JsonResponse({'error': 'Новое звание должно быть выше нынешного звания'}, status=400)

            if personsRankInfo.militaryRank.order + 1 != newRankInstance.order:
                return JsonResponse({'error': 'Новое звание должно быть следующим званием а не выше чем на 2 звания'}, status=400)

            if receivedType != 'Досрочное' and personsPositionInfo.position.maxRank.order >= newRankInstance.order:
                return JsonResponse({'error': 'Новое звание превышает максимальное звание должности'}, status=400)

            changedRankTitleKaz = newRankTitle
            if newRankTitle == 'старший лейтенант':
                changedRankTitleKaz = 'аға лейтенант'

            if not DecreeList.objects.filter(personId=personInstance, decreeType="Присвоение звания",
                                             isConfirmed=False).first():

                if receivedType == 'Досрочное':
                    time_difference = datetime.strptime(rankUpDate, "%Y-%m-%d").date() - personsRankInfo.receivedDate
                    half_promotion_days = personsRankInfo.militaryRank.nextPromotionDateInDays / 2
                    if time_difference >= timedelta(days=half_promotion_days):
                        decreeInstance = DecreeList.objects.create(
                            decreeType="Присвоение звания",
                            decreeDate=datetime.strptime(rankUpDate, "%Y-%m-%d").date(),
                            personId=personInstance
                        )

                        RankUpInfo.objects.create(
                            previousRank=personsRankInfo.militaryRank,
                            newRank=newRankInstance,
                            receivedType=receivedType,
                            decreeId=decreeInstance
                        )
                    else:
                        return JsonResponse({'error': 'Ошибка досрочного повышения: Дата повышения не равно или не '
                                                      'превышает половины даты'
                                                      ' последующего повышения'}, status=400)


            else:
                return JsonResponse({'error': 'У сотрудника уже имеется приказ о присвоении звания который не '
                                              'согласован'}, status=400)

            soglasnie = ['б', 'в', 'г', 'д', 'ж', 'з', 'й', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч',
                         'ш', 'щ']
            glasnie = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я']

            changedSurname = personInstance.surname
            changedFirstName = personInstance.firstName
            changedSurnameKaz = personInstance.surname
            changedPatronymic = personInstance.patronymic

            if personInstance.gender.genderName == 'Мужской':
                if personInstance.firstName[-1] in soglasnie:
                    changedFirstName = personInstance.firstName + 'у'
                else:
                    changedFirstName = personInstance.firstName

                if personInstance.surname[-2:] == 'ев' or personInstance.surname[-2:] == 'ов':
                    changedSurname = personInstance.surname + 'у'
                    changedSurnameKaz = personInstance.surname + 'қа'
                else:
                    changedSurname = personInstance.surname
                    changedSurnameKaz = personInstance.surname

            if personInstance.gender.genderName == 'Женский':
                if personInstance.firstName[-1] == 'а':
                    changedFirstName = personInstance.firstName[:-1]
                    changedFirstName = changedFirstName + 'е'
                else:
                    changedFirstName = personInstance.firstName

                if personInstance.surname[-3:] == 'ева' or personInstance.surname[-3:] == 'ова':
                    changedSurname = personInstance.surname[:-1]
                    changedSurname = changedSurname + 'ой'
                    changedSurnameKaz = personInstance.surname + 'ға'
                else:
                    changedSurname = personInstance.surname

                if personInstance.patronymic[-4:] == 'евна' or personInstance.patronymic[-4:] == 'овна':
                    changedPatronymic = personInstance.patronymic[:-1]
                    changedPatronymic = changedPatronymic + 'е'
                else:
                    changedPatronymic = personInstance.patronymic

            personsFIO = changedSurname + ' ' + changedFirstName + ' ' + changedPatronymic
            personsFIOKaz = personInstance.firstName + ' ' + personInstance.patronymic + ' ' + changedSurnameKaz

            changedCurrentDepartmentName = currentDepartment.DepartmentName
            changedCurrentDepartmentNameKaz = currentDepartment.DepartmentNameKaz
            changedCurrentPositionKaz = currentPosition.positionTitleKaz
            changedCurrentPosition = currentPosition.positionTitle

            words = currentDepartment.DepartmentName.split()
            if words[0] == 'Управление':
                words[0] = 'Управления'
                changedCurrentDepartmentName = ' '.join(words)

            if currentDepartment.DepartmentName == 'ЦА':
                changedCurrentDepartmentName = 'Управления'

            if currentDepartment.DepartmentName == 'ЦА':
                currentDepartment.DepartmentName = 'Управление'

            if currentDepartment.DepartmentNameKaz == 'Басқарма':
                changedCurrentDepartmentNameKaz = 'Басқармасының'
            else:
                changedCurrentDepartmentNameKaz = currentDepartment.DepartmentNameKaz + 'ның'

            if currentPosition.positionTitle == 'Руководитель департамента':
                changedCurrentPosition = 'Руководителю департамента'

            if currentPosition.positionTitle == 'Заместитель руководителя департамента':
                changedCurrentPosition = 'Заместителю руководителя департамента'

            if currentPosition.positionTitle == 'Руководитель управления':
                changedCurrentPosition = 'Руководителю управления'

            if currentPosition.positionTitle == 'Заместитель руководителя управления':
                changedCurrentPosition = 'Заместителю руководителя управления'

            if currentPosition.positionTitle == 'Оперуполномоченный по особо важным делам':
                changedCurrentPosition = 'Оперуполномоченному по особо важным делам'

            if currentPosition.positionTitle == 'Старший оперуполномоченный':
                changedCurrentPosition = 'Старшему оперуполномоченному'

            if currentPosition.positionTitle == 'Оперуполномоченный':
                changedCurrentPosition = 'Оперуполномоченному'

            if currentPosition.positionTitleKaz == 'Аға жедел уәкіл':
                changedCurrentPositionKaz = 'Аға жедел уәкілі'
            if currentPosition.positionTitleKaz == 'Жедел уәкіл':
                changedCurrentPositionKaz = 'Жедел уәкілі'
            if currentPosition.positionTitleKaz == 'Аса маңызды істер жөніндегі жедел уәкіл':
                changedCurrentPositionKaz = 'Аса маңызды істер жөніндегі жедел уәкілі'

            changedCurrentPosition = changedCurrentPosition.lower()
            changedCurrentPositionKaz = changedCurrentPositionKaz.lower()

            year, month, day = map(int, rankUpDate.split('-'))
            day = int(day)
            monthString = None
            monthStringKaz = None

            if month == 1:
                monthString = 'января'
                monthStringKaz = 'қантардан'
            if month == 2:
                monthString = 'февраля'
                monthStringKaz = 'ақпаннан'
            if month == 3:
                monthString = 'марта'
                monthStringKaz = 'наурыздан'
            if month == 4:
                monthString = 'апреля'
                monthStringKaz = 'сәуірден'
            if month == 5:
                monthString = 'мая'
                monthStringKaz = 'мамырдан'
            if month == 6:
                monthString = 'июня'
                monthStringKaz = 'маусымнан'
            if month == 7:
                monthString = 'июля'
                monthStringKaz = 'шілдеден'
            if month == 8:
                monthString = 'августа'
                monthStringKaz = 'тамыздан'
            if month == 9:
                monthString = 'сентября'
                monthStringKaz = 'қыркүйектен'
            if month == 10:
                monthString = 'октября'
                monthStringKaz = 'қазаннан'
            if month == 11:
                monthString = 'ноября'
                monthStringKaz = 'қарашадан'
            if month == 12:
                monthString = 'декабря'
                monthStringKaz = 'желтоқсаннан'

            changedDateKaz = str(year) + ' жылғы ' + str(day) + ' ' + monthStringKaz
            changedDate = str(day) + ' ' + monthString + ' ' + str(year) + ' ' + 'года'

            base = 'представление'
            baseKaz = 'ұсыныс'

            # Load the Word document template
            template_path = 'docx_generator/static/templates/rankup_template.docx'  # Update with the path to your template
            document = Document(template_path)

            # Define a function to replace placeholders in the document
            def replace_placeholder(placeholder, replacement):
                for paragraph1 in document.paragraphs:
                    if placeholder in paragraph1.text:

                        for run1 in paragraph1.runs:
                            if placeholder in run1.text:
                                run1.text = run1.text.replace(placeholder, replacement)
                                run1.font.size = Pt(14)  # Adjust the font size if needed
                                run1.font.name = 'Times New Roman'

            # Replace placeholders with actual data
            replace_placeholder('NEWRANK', f"{changedRankTitleKaz}")
            replace_placeholder('CURRENTD', f"{changedCurrentDepartmentNameKaz}")
            replace_placeholder('CURRENTP', f"{changedCurrentPositionKaz}")
            replace_placeholder('FIO', f"{personsFIOKaz}")
            replace_placeholder('DATE', f"{changedDateKaz}")
            replace_placeholder('BASE', baseKaz)

            replace_placeholder('newrank', f"{newRankTitle}")
            replace_placeholder('currentp', f"{changedCurrentPosition}")
            replace_placeholder('currentd', f"{changedCurrentDepartmentName}")
            replace_placeholder('fio', f"{personsFIO}")
            replace_placeholder('date', f"{changedDate}")
            replace_placeholder('base', base)

            doc_stream = BytesIO()
            document.save(doc_stream)
            doc_stream.seek(0)

            # Prepare the HTTP response with the modified document
            response = HttpResponse(doc_stream.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml'
                                                 '.document')
            response['Content-Disposition'] = f'attachment; filename=Приказ о присвоении.docx'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
