from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Photo
from .serializers import PhotoSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (IsAuthenticated,)
