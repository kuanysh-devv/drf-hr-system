from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from docx_generator.views import *
from birth_info.views import *
from decree.views import *
from education.views import *
from filter import views
from filter.views import attestation_list_view, attestation_list_view_download, rankUps_list_view, \
    rankUps_list_view_download, pension_list_view, pension_list_view_download
from identity_card_info.views import *
from location.views import *
from military_rank.views import *
from person.views import *
from photo.views import *
from position.views import *
from resident_info.views import *
from rest_framework import routers

from staffing_table.views import StaffingTableViewSet, getStaffingTable, downloadStaffingTable
from working_history.views import WorkingHistoryViewSet

router = routers.DefaultRouter()
router.register(r'birth-info', BirthInfoViewSet)
router.register(r'decree-list', DecreeListViewSet)
router.register(r'spec-check', SpecCheckViewSet)
router.register(r'sick-leave', SickLeaveViewSet)
router.register(r'education', EducationViewSet)
router.register(r'investigation', InvestigationViewSet)
router.register(r'course', CourseViewSet)
router.register(r'attestation', AttestationViewSet)
router.register(r'academic-degree', AcademicDegreeViewSet)
router.register(r'identity-card-info', IdentityCardInfoViewSet)
router.register(r'location', LocationViewSet)
router.register(r'department', DepartmentViewSet)
router.register(r'military-rank', MilitaryRankViewSet)
router.register(r'rank-info', RankInfoViewSet)
router.register(r'person', PersonViewSet)
router.register(r'gender', GenderViewSet)
router.register(r'family-status', FamilyStatusViewSet)
router.register(r'relative', RelativeViewSet)
router.register(r'family-composition', FamilyCompositionViewSet)
router.register(r'class-category', ClassCategoryViewSet)
router.register(r'autobiography', AutobiographyViewSet)
router.register(r'reward', RewardViewSet)
router.register(r'language-skill', LanguageSkillViewSet)
router.register(r'sport-skill', SportSkillViewSet)
router.register(r'photo', PhotoViewSet)
router.register(r'position', PositionViewSet)
router.register(r'position-info', PositionInfoViewSet)
router.register(r'working-history', WorkingHistoryViewSet)
router.register(r'residentinfo', ResidentInfoViewSet)
router.register(r'staffing-table', StaffingTableViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/filter/', views.filter_data, name='filter_data'),
    path('api/v1/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/change_password/', change_password, name='change_password'),
    path('generate_work_reference/<int:person_id>/', generate_work_reference, name='generate_work_reference'),
    path('api/v1/generate-appointment-decree/', generate_appointment_decree, name='generate_appointment_decree'),
    path('api/v1/generate-transfer-decree/', generate_transfer_decree, name='generate_transfer_decree'),
    path('api/v1/persons_by_department/', departments_persons, name='persons_by_department'),
    path('api/v1/staffing_table/', getStaffingTable, name='staffing_table'),
    path('api/v1/location_departments/<str:location_name>/', departments_by_location, name='departments_by_location'),
    path('api/v1/positions_departments/<int:department_id>/', positions_by_department, name='positions_by_department'),
    path('api/v1/close_attestations/', attestation_list_view, name='attestation-list'),
    path('api/v1/close_attestations_download/', attestation_list_view_download, name='attestation-list_download'),
    path('api/v1/rank-up-list/', rankUps_list_view, name='rankUps_list_view'),
    path('api/v1/rank-up-list-download/', rankUps_list_view_download, name='rankUps_list_view_download'),
    path('api/v1/download-staffing-table/', downloadStaffingTable, name='downloadStaffingTable'),
    path('api/v1/get-rank-up-info/', get_rank_up_info, name='get_rank_up_info'),
    path('api/v1/get-available-pin/', getAvailableLastPin, name='getAvailableLastPin'),
    path('api/v1/pension-list-view/', pension_list_view, name='pension_list_view'),
    path('api/v1/pension-list-download/', pension_list_view_download, name='pension_list_view_download'),
    path('api/v1/get-decree-list', getDecreeList, name='getDecreeList'),
    path('api/v1/get-transfer-info', getTransferInfo, name='getTransferInfo'),
    path('api/v1/get-rankup-info', getRankUpInfo, name='getRankUpInfo'),
    path('api/v1/cancel-transfer/', cancelTransfer, name='cancelTransfer'),
    path('api/v1/cancel-rankup/', cancelRankUp, name='cancelRankUp'),
    path('api/v1/search_persons/', search_persons, name='search_persons'),
    path('api/v1/generate-rankup-decree/', generate_rankup_decree, name='generate_rankup_decree'),
]
