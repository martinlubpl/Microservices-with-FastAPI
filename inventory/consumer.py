
from main import redis, Product
import time

key = "order_completed"

group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists")

while True:
    try:
        response = redis.xreadgroup(group, key, {key: '>'}, None)
        if response != []:
            for result in response:
                obj = result[1][0][1]
                product = Product.get(obj['product_id'])
                print(product)
                product.quantity_avail -= int(obj['quantity'])
                product.save()

    except Exception as e:
        print(str(e))

    time.sleep(1)
