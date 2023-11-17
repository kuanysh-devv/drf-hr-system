from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Pt
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from education.serializers import EducationSerializer, AcademicDegreeSerializer
from person.models import Person
from photo.models import Photo
from position.models import PositionInfo
from birth_info.models import BirthInfo
from education.models import Education, AcademicDegree
import base64, io
from docx.shared import Inches
from working_history.models import WorkingHistory


@csrf_exempt
def generate_work_reference(request, person_id):
    # Fetch the necessary data
    person = get_object_or_404(Person, pk=person_id)
    birth_info = BirthInfo.objects.get(personId=person)
    birth_date = str(birth_info.birth_date)
    birth_date_format = datetime.strptime(birth_date, '%Y-%m-%d')
    formatted_date = birth_date_format.strftime('%d.%m.%Y')

    education_objects = Education.objects.filter(personId=person.id)
    education_data = EducationSerializer(education_objects, many=True).data
    first_education = education_data[0]
    date_edu_string = first_education['educationDateOut']  # Assuming 'first_education' is an OrderedDict
    date_obj = datetime.strptime(date_edu_string, '%Y-%m-%d')

    academic_degrees_objects = AcademicDegree.objects.filter(personId=person.id)
    academic_degrees_data = AcademicDegreeSerializer(academic_degrees_objects, many=True).data
    first_academic_degree = academic_degrees_data[0]
    date_academ_string = first_academic_degree['academicDiplomaDate']
    date_academ_obj = datetime.strptime(date_academ_string, '%Y-%m-%d')

    persons_photo = Photo.objects.get(personId=person)
    photo_base64 = persons_photo.photoBinary

    # Replace with your photo field
    photo_binary = base64.b64decode(photo_base64)
    image = io.BytesIO(photo_binary)

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
                    print(run1.text)
                    if placeholder in run1.text:
                        run1.text = run1.text.replace(placeholder, replacement)
                        run1.font.size = Pt(12)  # Adjust the font size if needed

    # Replace placeholders with actual data
    replace_placeholder('Name', f"{person.firstName}")
    replace_placeholder('surname', f"{person.surname}")
    replace_placeholder('patronymic', f"{person.patronymic}")
    replace_placeholder('nationality', f"{person.nationality}")
    replace_placeholder('position', person.positionInfo.position.positionTitle)
    replace_placeholder('iin', person.iin)
    replace_placeholder('birth_date', str(formatted_date))
    replace_placeholder('region', birth_info.region)
    replace_placeholder('city', birth_info.city)
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
