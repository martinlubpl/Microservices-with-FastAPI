from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests

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


@app.post("/new_order")
async def create_order(request: Request):
    """create new order"""

    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' %
                       body['product_id'])
    return req.json()
