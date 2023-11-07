from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from birth_info.views import *
from decree.views import *
from education.views import *
from filter import views
from identity_card_info.views import *
from location.views import *
from military_rank.views import *
from person.views import *
from photo.views import *
from position.views import *
from resident_info.views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'birth-info', BirthInfoViewSet)
router.register(r'decree-list', DecreeListViewSet)
router.register(r'spec-check', SpecCheckViewSet)
router.register(r'sick-leave', SickLeaveViewSet)
router.register(r'education', EducationViewSet)
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/filter/', views.filter_data, name='filter_data'),
    path('api/v1/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
