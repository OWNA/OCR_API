from __future__ import unicode_literals

from django.db import models
import datetime
import uuid
import os


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('photos', filename)


class AnalyzedImage(models.Model):
    user_uid = models.CharField(
        "Unique Identification of the user", max_length=128)
    uploaded_at = models.DateTimeField(default=datetime.datetime.now)
    matching_order_id = models.CharField(
        "Order ID", max_length=254, null=True)
    confidence_score = models.FloatField(null=True)
    webhook_url = models.URLField("webhook url", max_length=1000, null=True)
    orders = models.TextField("user orders")
    wholesalers = models.TextField("available wholesalers products", null=True)
    metrics = models.TextField("metrics computed on client", null=True)
    rotation = models.FloatField(default=0)
    status = models.CharField(
        "Status of the analysis", max_length=25, default="PENDING")


class Structure(models.Model):
    uploaded_at = models.DateTimeField(default=datetime.datetime.now)
    webhook_url = models.URLField("webhook url", max_length=1000, null=True)
    status = models.CharField(
        "Status of the analysis", max_length=25, default="PENDING")


class File(models.Model):
    url = models.FileField(upload_to=get_file_path, max_length=254)
    rotation = models.FloatField(default=0)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE,
                                  related_name="urls", null=True)
    image = models.ForeignKey(AnalyzedImage, on_delete=models.CASCADE,
                              related_name="urls", null=True)


class Item(models.Model):
    description = models.CharField("Product description", max_length=1000, null=True)
    code = models.CharField("Product code", max_length=100, null=True)
    unit_of_measure = models.CharField("Unit Of Measure", max_length=100, null=True)
    pack_size = models.CharField("Pack Size", max_length=100, null=True)
    brand = models.CharField("Brand", max_length=100, null=True)
    order_item_id = models.CharField("Order Item ID", max_length=254, null=True)
    quantity = models.FloatField()
    unit_price_pre_gst = models.FloatField()
    unit_price = models.FloatField()
    price_pre_gst = models.FloatField()
    price = models.FloatField()
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE,
                                  related_name="items", null=True)
    image = models.ForeignKey(AnalyzedImage, on_delete=models.CASCADE,
                              related_name="items", null=True)


class ItemChange(models.Model):
    change_type = models.CharField("Change type", max_length=128)
    expected_value = models.FloatField(null=True)
    value = models.FloatField(null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="changes")
