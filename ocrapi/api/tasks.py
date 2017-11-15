from __future__ import absolute_import, unicode_literals
from celery import shared_task, task
import requests
import logging
import tempfile
import os
import json
import urllib
import traceback
import magic
from tabulate import tabulate
from PIL import Image

from matching.optimizer import optimizeMatching
from abbyy.process import recognizeFile
from abbyy.AbbyyOnlineSdk import ProcessingSettings
from utils.files import XMLFile, SimpleWord
from utils.pdf import PDFFile
from utils.util import get_price_values, getFloat, index
from utils.items import OrderedItem
from matching.exceptions import *
from table.segmenter import segment_and_label_from_raw_ocr
from table.pdf import segment_and_label_pdf
from rest_framework.renderers import JSONRenderer

from ocrapi.api.parser import parse_orders
from ocrapi.api.order_match import find_best_soft_match
from ocrapi.api.models import AnalyzedImage, Item, ItemChange, Structure
from ocrapi.api.serializers import AnalyzedImageSerializer, StructureSerializer
from django.conf import settings


logger = logging.getLogger("tasks")


def has_changed(expected_value, value):
    return abs(value - expected_value) > 0.01 * expected_value


def record_quantity_change(item, quantity, productItem):
    change = ItemChange(
        change_type="QUANTITY_CHANGED",
        expected_value=productItem.quantity,
        value=quantity,
        item=item
    )
    change.save()
    logger.debug('Change in quantity for %s from %s to %s',
                 productItem, productItem.quantity, quantity)


def record_price_change(item, price, productItem):
    change = ItemChange(
        change_type="UNIT_PRICE_CHANGED",
        expected_value=productItem.totalUnitPrice,
        value=price,
        item=item
    )
    change.save()
    logger.debug('Change in price for %s from %s to %s',
                 productItem, productItem.totalUnitPrice, price)


def record_new_item(item):
    change = ItemChange(
        change_type="NEW_ITEM",
        item=item
    )
    change.save()
    logger.debug('New item %s', item)


def record_missing(image, productItem):
    item = Item(description=productItem.description,
                quantity=0,
                unit_price_pre_gst=productItem.unitPrice,
                unit_price=productItem.totalUnitPrice,
                price_pre_gst=0,
                price=0,
                image=image)
    item.save()
    change = ItemChange(
        change_type="MISSING_ITEM",
        expected_value=productItem.quantity,
        value=0,
        item=item
    )
    change.save()
    logger.debug('Missing item %s', productItem)


def run_abbyy(image_url):
    # Run ABBYY analysis
    with tempfile.NamedTemporaryFile(dir='/tmp',
                                     suffix='.xml',
                                     delete=False) as tmpfile:
        xml_filename = tmpfile.name
    processing_settings = ProcessingSettings()
    processing_settings.Language = 'English'
    processing_settings.OutputFormat = 'xmlForCorrectedImage,txt'
    processing_settings.withVariants = True
    processing_settings.Profile = 'textExtraction'
    recognizeFile(image_url, xml_filename, processing_settings)
    text_filename = xml_filename + '2'
    return xml_filename, text_filename


def rotate_file(obj, rotation):
    if rotation:
        obj.rotation = rotation
        image_url = os.path.join(settings.MEDIA_ROOT, str(obj.url))
        image_content = Image.open(image_url).rotate(-rotation, expand=1)
        image_content.save(image_url)
        obj.save()


def process_image_unsafe(image):
    logger.debug("Processing image with ID %s and User ID %s",
                 image.id, image.user_uid)
    image.items.all().delete()

    words = []
    page_index = 0
    for file_obj in image.urls.all():
        file_url = os.path.join(settings.MEDIA_ROOT, str(file_obj.url))
        file_type = magic.from_file(file_url, mime=True)
        if file_type == 'image/jpeg':
            xml_filename, _ = run_abbyy(file_url)
            xmlFile = XMLFile(xml_filename, page_index=page_index)
            xmlFile.parseWithVariants()
            rotate_file(file_obj, xmlFile.rotation)
            words += xmlFile.words
            page_index += 1
        elif file_type == 'application/pdf':
            pdf_file = PDFFile(file_url, offset=page_index)
            pdf_file.parse()
            words += pdf_file.words
            page_index += pdf_file.page_count
        else:
            raise UnsupportedFileType()
    params = {'user_uid': image.user_uid}
    url = '{}?{}'.format(settings.ORDERS_API_URL, urllib.urlencode(params))
    headers = {
        'Authorization': 'Token ' + os.environ['OCR_SERVER_TOKEN']
    }
    orders = parse_orders(json.loads(image.orders))
    distance, (order_id, originalItems) = find_best_soft_match(orders, words)
    logger.debug('Found matching item %s at %s in Jaccard distance',
                 order_id, distance)
    image.confidence_score = int(100 - distance * 100) / 100.
    image.matching_order_id = order_id

    # Run matching
    bestCost, bestAssignment = optimizeMatching(words, originalItems)
    descriptionIndex = bestAssignment.descriptionIndex
    quantityIndex = bestAssignment.quantityIndex
    priceIndex = bestAssignment.priceIndex
    valuePart = bestAssignment.relevantParts[priceIndex]
    matching = bestAssignment.matching
    for lineIndex, productItem in enumerate(originalItems):

        matchingDescription = matching[lineIndex][descriptionIndex]
        matchingQuantity = matching[lineIndex][quantityIndex]
        matchingPrice = matching[lineIndex][priceIndex]

        if not len(matchingDescription):
            record_missing(image, productItem)
            continue

        quantity = float(matchingQuantity[0].value)
        description = matchingDescription[0].value
        price_value = float(matchingPrice[0].value)

        if not quantity:
            record_missing(image, productItem)
            continue

        price, unit_price, price_pre_gst, unit_price_pre_gst = get_price_values(
            price_value, valuePart, quantity, productItem.gstPercent)
        item = Item(description=description,
                    quantity=quantity,
                    unit_price_pre_gst=unit_price_pre_gst,
                    unit_price=unit_price,
                    price_pre_gst=price_pre_gst,
                    order_item_id=productItem.item_id,
                    price=price,
                    image=image)
        item.save()
        if has_changed(quantity, productItem.quantity):
            record_quantity_change(item, quantity, productItem)
        if has_changed(unit_price, productItem.totalUnitPrice):
            record_price_change(item, unit_price, productItem)
    for item in matching[len(originalItems):]:
        matchingDescription = item[descriptionIndex]
        matchingQuantity = item[quantityIndex]
        matchingPrice = item[priceIndex]
        quantity = float(matchingQuantity[0].value)
        description = matchingDescription[0].value
        price_value = float(matchingPrice[0].value)

        price, unit_price, price_pre_gst, unit_price_pre_gst = get_price_values(
            price_value, valuePart, quantity, 0)
        item = Item(description=description,
                    quantity=quantity,
                    unit_price_pre_gst=unit_price_pre_gst,
                    unit_price=unit_price,
                    price_pre_gst=price_pre_gst,
                    order_item_id=None,
                    price=price,
                    image=image)
        item.save()
        record_new_item(item)
        item.save()



def report_webhook(image, serializer):
    serializer = serializer(image)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(image.webhook_url,
                      headers=headers,
                      data=JSONRenderer().render(serializer.data))

@task
def process_image(image_id):
    logger.debug("Processing image with ID %s", image_id)
    image = AnalyzedImage.objects.filter(id=image_id).get()
    try:
        process_image_unsafe(image)
    except NoMatchingOrder as e:
        image.status = 'NO_MATCHING_ORDER'
    except MaxDurationReached as e:
        image.status = 'DEADLINE_EXCEEDED'
    except UnsupportedFileType as e:
        image.status = 'UNSUPPORTED_FORMAT'
    except Exception as e:
        logger.error(traceback.format_exc())
        image.status = 'FAILED'
    else:
        image.status = 'PROCESSED'
    image.save()
    if image.webhook_url:
        report_webhook(image, AnalyzedImageSerializer)
    return image.status


def extract_structure_unsafe_single_file(structure, file_obj):
    file_url = os.path.join(settings.MEDIA_ROOT, str(file_obj.url))
    logger.debug("Processing structure from %s", file_url)
    file_type = magic.from_file(file_url, mime=True)

    if file_type == 'image/jpeg':
        xml_filename, text_filename = run_abbyy(file_url)
        xmlFile = XMLFile(xml_filename)
        xmlFile.parseWithVariants(split=True)
        rotate_file(file_obj, xmlFile.rotation)
        f = open(text_filename)
        lines = []
        for line in f.readlines():
            if line.strip():
                lines.append(line.strip())
        table, headers = segment_and_label_from_raw_ocr(lines, xmlFile.words)
    elif file_type == 'application/pdf':
        table, headers = segment_and_label_pdf(file_url)
    else:
        raise UnsupportedFileType()

    def get_value(headers, header_name, line):
        header_index = index(headers, header_name)
        return line[header_index] if header_index != -1 else ''

    def get_float_value(headers, header_name, line):
        return getFloat(get_value(headers, header_name, line))

    for line in table:
        unit_price_pre_gst = get_float_value(headers, 'price1', line)
        unit_price = get_float_value(headers, 'price1', line)
        price_pre_gst = get_float_value(headers, 'price3', line)
        price = get_float_value(headers, 'price4', line)
        quantity = get_float_value(headers, 'quantity', line)
        description = get_value(headers, 'description', line)
        code = get_value(headers, 'code', line)
        brand = get_value(headers, 'brand', line)
        unit_of_measure = get_value(headers, 'unitOfMeasure', line)
        pack_size = get_value(headers, 'packSize', line)
        # Update total price values
        if price and not price_pre_gst:
            price_pre_gst = price
        elif price_pre_gst and not price:
            price = price_pre_gst
        # Update unit price values
        if quantity and price and not unit_price and not unit_price_pre_gst:
            unit_price = price / quantity
        if unit_price and not unit_price_pre_gst:
            unit_price_pre_gst = unit_price
        elif unit_price_pre_gst and not unit_price:
            unit_price = unit_price_pre_gst
        item = Item(description=description,
                    code=code,
                    unit_of_measure=unit_of_measure,
                    pack_size=pack_size,
                    brand=brand,
                    quantity=quantity,
                    unit_price_pre_gst=unit_price_pre_gst,
                    price_pre_gst=price_pre_gst,
                    unit_price=unit_price,
                    price=price,
                    structure=structure)
        item.save()
    logger.debug(tabulate(table, headers))


def extract_structure_unsafe(structure):
    structure.items.all().delete()
    for file_obj in structure.urls.all():
        extract_structure_unsafe_single_file(structure, file_obj)


@task
def extract_structure(structure_id):
    logger.debug("Extracting structure with ID %s", structure_id)
    structure = Structure.objects.filter(id=structure_id).get()
    try:
        extract_structure_unsafe(structure)
    except UnsupportedFileType as e:
        logger.error(traceback.format_exc())
        structure.status = 'UNSUPPORTED_FORMAT'
    except Exception as e:
        logger.error(traceback.format_exc())
        structure.status = 'FAILED'
    else:
        structure.status = 'PROCESSED'
    structure.save()
    if structure.webhook_url:
        report_webhook(structure, StructureSerializer)
    return structure.status
