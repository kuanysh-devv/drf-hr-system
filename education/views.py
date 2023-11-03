from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Education, Course, Attestation
from .serializers import EducationSerializer, CourseSerializer, AttestationSerializer


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = (IsAuthenticated,)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)


class AttestationViewSet(viewsets.ModelViewSet):
    queryset = Attestation.objects.all()
    serializer_class = AttestationSerializer
    permission_classes = (IsAuthenticated,)
