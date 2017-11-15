import json
from utils.loader import loadData

orders, _ = loadData('data/original/B.csv')

fixture = []

items = {}

for order_id, order in enumerate(orders):
    fixture.append({
        'model': 'remote.Order',
        'fields': {
            'id': (order_id + 1),
            'user_uid': order_id // 10
        }
    })
    for item in order:
        items[item.code] = item
        fixture.append({
            'model': 'remote.Item',
            'fields': {
                'order_id': (order_id + 1),
                'description': item.description,
                'code': item.code,
                'quantity': item.quantity,
                'unit_price_pre_gst': item.unitPrice,
                'unit_price': item.totalUnitPrice,
                'price_pre_gst': item.price,
                'price': item.totalPrice
            }
        })

fixture.append({
    'model': 'remote.Wholesaler',
    'fields': {
        'id': 1,
        'name': 'Wholesales Solutions'
    }
})

for item in items.values():
    fixture.append({
        'model': 'remote.WholesalerItem',
        'fields': {
            'description': item.description,
            'unit_price_pre_gst': item.unitPrice,
            'unit_price': item.totalUnitPrice,
            'wholesaler_id': 1
        }
    })

print json.dumps(fixture, indent=4)
