import json
import logging
from utils.items import OrderedItem

logger = logging.getLogger("tasks")

def get_float(value):
    try:
        return float(value)
    except Exception:
        return 0

def parse_orders(response):
    orders = []
    if 'results' in response:
        response = response['results']
    for result in response:
        try:
            items = []
            for item in result['items']:
                items.append(OrderedItem(
                    item.get('order_item_id', ''),
                    item.get('code', ''),
                    item.get('description', ''),
                    '', # brand
                    '', # packSize
                    '', # unitOfMeasure
                    get_float(item.get('unit_price_pre_gst', 0)),
                    get_float(item.get('unit_price', 0)),
                    get_float(item.get('price_pre_gst', 0)),
                    get_float(item.get('price', 0)),
                    get_float(item.get('quantity', 0))
                ))
            orders.append([result['id'], items])
        except Exception as e:
            logger.warn('Failed to parse %s as %r', result, e)
    return orders
