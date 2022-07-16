from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# this should be separate db. each microservice should have its own db!
# free plan of redis cloud is limited to 1 db only so ¯\_(ツ)_/¯
redis = get_redis_connection(
    # public endpoint from redis cloud
    host="redis-14251.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=14251,
    password="cRkTVn00bj1BDQvqpB91Kq5aicZt2hdX",
    decode_responses=True,
)


class Order(HashModel):
    """Order class"""
    product_id: str
    quantity: int
    price: float
    fee: float
    total: float
    status: str  # choice from ["pending", "paid", "refunded"]

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def all_orders(pk: str):
    return Order.get(pk)


@app.post("/orders")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    """create new order"""

    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' %
                       body['product_id'])
    product = req.json()
    order = Order(
        product_id=body['product_id'],
        quantity=body['quantity'],
        price=product['price'],
        fee=product['price'] * 0.1,  # 10% fee
        total=product['price'] * 1.1,
        status='pending'
    )

    order.save()
    background_tasks.add_task(order_completed, order)

    # order_completed(order)
    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'paid'
    order.save()
