from ocrapi.api.models import AnalyzedImage, Item, ItemChange, Structure, File
from rest_framework import serializers
import json


class ItemChangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemChange
        fields = ('expected_value', 'change_type', 'value')


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('description', 'quantity', 'code',
                  'unit_price_pre_gst', 'unit_price',
                  'pack_size', 'unit_of_measure', 'brand',
                  'price_pre_gst', 'price')


class StructureItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('description', 'quantity', 'code',
                  'unit_price_pre_gst', 'unit_price',
                  'pack_size', 'unit_of_measure', 'brand',
                  'price_pre_gst', 'price')


class FileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = File
        fields = ('url', 'rotation')


class StructureSerializer(serializers.HyperlinkedModelSerializer):

    items = StructureItemSerializer(many=True, read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    files = serializers.ListField(
        child=serializers.FileField(max_length=100000,
                                    allow_empty_file=False,
                                    use_url=False),
        write_only=True,
        min_length=1)
    urls = FileSerializer(many=True, read_only=True)

    id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        files = validated_data.pop('files')
        structure = Structure.objects.create(**validated_data)
        for url in files:
            File.objects.create(url=url, structure=structure)
        return structure

    class Meta:
        model = Structure
        fields = ('uploaded_at', 'urls', 'status', 'id', 'items',
                  'webhook_url', 'files')


class AnalyzedImageSerializer(serializers.HyperlinkedModelSerializer):

    items = ItemSerializer(many=True, read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    confidence_score = serializers.FloatField(read_only=True)
    matching_order_id = serializers.IntegerField(read_only=True)
    orders = serializers.CharField(write_only=True, allow_blank=True)
    wholesalers = serializers.CharField(write_only=True, allow_blank=True)
    metrics = serializers.CharField(write_only=True, allow_blank=True)
    urls = FileSerializer(many=True, read_only=True)
    files = serializers.ListField(
        child=serializers.FileField(max_length=100000,
                                    allow_empty_file=False,
                                    use_url=False),
        write_only=True,
        min_length=1)

    def create(self, validated_data):
        files = validated_data.pop('files')
        image = AnalyzedImage.objects.create(**validated_data)
        for url in files:
            File.objects.create(url=url, image=image)
        return image

    class Meta:
        model = AnalyzedImage
        fields = ('user_uid', 'uploaded_at', 'urls', 'status', 'id',
                  'items', 'confidence_score', 'matching_order_id',
                  'webhook_url', 'orders', 'wholesalers', 'metrics', 'files')


class FormattedJsonField(serializers.CharField):

    def to_representation(self, obj):
        try:
            obj_json = json.loads(obj)
            return obj_json
        except Exception as e:
            print e
        return obj


class AnalyzedImageDebugSerializer(serializers.HyperlinkedModelSerializer):

    items = ItemSerializer(many=True, read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    user_uid = serializers.CharField(read_only=True)
    webhook_url = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    confidence_score = serializers.FloatField(read_only=True)
    rotation = serializers.FloatField(read_only=True)
    matching_order_id = serializers.IntegerField(read_only=True)
    orders = FormattedJsonField(read_only=True)
    wholesalers = FormattedJsonField(read_only=True)
    metrics = FormattedJsonField(read_only=True)
    urls = FileSerializer(many=True, read_only=True)

    class Meta:
        model = AnalyzedImage
        fields = ('user_uid', 'uploaded_at', 'urls', 'status', 'id', 'items',
                  'confidence_score', 'matching_order_id', 'webhook_url',
                  'orders', 'wholesalers', 'metrics', 'rotation')
