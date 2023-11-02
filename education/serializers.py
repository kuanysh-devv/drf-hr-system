from rest_framework import serializers

from .models import Education, Course, Attestation


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
