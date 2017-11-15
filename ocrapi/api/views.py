from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from ocrapi.api.serializers import AnalyzedImageSerializer,\
    AnalyzedImageDebugSerializer, StructureSerializer
from ocrapi.api.models import AnalyzedImage, Structure
from ocrapi.api.tasks import process_image, extract_structure
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import Http404


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class AnalyzedImageViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    API endpoint that allows invoice images to be viewed or modified.
    """
    serializer_class = AnalyzedImageSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)

    def get_queryset(self):
        queryset = AnalyzedImage.objects.all().order_by('-uploaded_at')
        user_uid = self.request.query_params.get('user_uid', None)
        if user_uid is not None:
            queryset = queryset.filter(user_uid=user_uid)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        process_image.delay(instance.id)
        return instance

    def create(self, request, *args, **kwargs):
        qd = request.data
        if 'files[]' in qd:
            items = qd.pop('files[]')
            for item in items:
                qd.update({'files': item})
        if 'url' in qd:
            item = qd.pop('url')[0]
            qd.update({'files': item})
        return super(AnalyzedImageViewSet, self).create(request, *args, **kwargs)

    @detail_route(methods=['get'])
    def process(self, request, pk):
        image = self.get_object()
        process_image.delay(image.id)
        serializer = AnalyzedImageSerializer(image)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def debug(self, request, pk):
        image = self.get_object()
        serializer = AnalyzedImageDebugSerializer(image)
        return Response(serializer.data)


class StructureViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    API endpoint that allows structure to be extracted from invoices.
    """
    serializer_class = StructureSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)

    def get_queryset(self):
        queryset = Structure.objects.all().order_by('-uploaded_at')
        user_uid = self.request.query_params.get('user_uid', None)
        if user_uid is not None:
            queryset = queryset.filter(user_uid=user_uid)
        return queryset

    def create(self, request, *args, **kwargs):
        qd = request.data
        if 'files[]' in qd:
            items = qd.pop('files[]')
            for item in items:
                qd.update({'files': item})
        return super(StructureViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        extract_structure.delay(instance.id)
        return instance

    @detail_route(methods=['get'])
    def process(self, request, pk):
        structure = self.get_object()
        extract_structure.delay(structure.id)
        serializer = StructureSerializer(structure)
        return Response(serializer.data)
