import unittest

from ocrapi.api.parser import parse_orders


class OrderParser(unittest.TestCase):

    def test_null_price(self):
        orders = parse_orders([
            {
                "id": 1,
                "status": "pending",
                "items": [
                    {
                        "code": "08-PILLARS",
                        "description": "Pizza Box Pillars",
                        "unit_price_pre_gst": "0.0",
                        "price": "0.0",
                        "price_pre_gst": "0.0",
                        "unit_price": "0.0",
                        "order_item_id": 1524,
                        "quantity": 1
                    }
                ]
            }
        ])
        self.assertEquals(1, len(orders))

if __name__ == '__main__':
    unittest.main()
