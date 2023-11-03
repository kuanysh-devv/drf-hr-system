from rest_framework import serializers

from .models import Education, Course, Attestation, AcademicDegree


class AttestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attestation
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class AcademicDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicDegree
        fields = "__all__"
