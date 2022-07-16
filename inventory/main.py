from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    # public endpoint from redis cloud
    host="redis-14251.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=14251,
    password="cRkTVn00bj1BDQvqpB91Kq5aicZt2hdX",
    decode_responses=True,
)


class Product(HashModel):
    """create product class"""
    name: str
    price: float
    quantity_avail: int

    class Meta:
        database = redis


@app.get("/products")
def all_products():
    """get all products"""
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    """helper function to format product for all_products"""
    product = Product.get(pk)
    return {
        "id": pk,
        "name": product.name,
        "price": product.price,
        "quantity_avail": product.quantity_avail
    }


@app.post("/products")
def create(product: Product):
    return product.save()


@app.get("/products/{pk}")
def get_product(pk: str):
    """get one product by pk"""
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete_product(pk: str):
    """delete one product by pk"""
    # product = Product.get(pk)
    return Product.delete(pk)
