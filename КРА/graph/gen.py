from typing import List, Iterable, Tuple
from faker import Faker
from .data import *
from functools import lru_cache
# import requests
# from bs4 import BeautifulSoup
from random import randint, choices as rchoices, sample as rsample
from utils import PositiveInt
from .tags import tags
from .game_names import game_names
from datetime import datetime, date


_faker = Faker()

class NoneIdException(Exception):
    def __init__(self):
        super().__init__('id must not be None in gen')

def gen_products(
    publishers: List[Publisher],
    n: PositiveInt
) -> Iterable[Product]:
    for i in range(n):
        yield Product(
            id = None,
            name= game_names[_faker.pyint(0, len(game_names)-1)],
            description = _faker.text(),
            price = _faker.pydecimal(max_value=5000, positive=True, right_digits=2),
            publisher_id = publishers[_faker.pyint(0, len(publishers)-1)].id,
            reviews_count = 0,
            rating_sum = 0
        )


def gen_publishers(n: PositiveInt) -> Iterable[Publisher]:
    for i in range(n):
        yield Publisher(
            id = None,
            name = _faker.company(),
            description = _faker.bs(),
            bank_account = _faker.aba()
        )


def gen_purchases(
    all_products: List[Product],
    user: User,
) -> Iterable[Purchase]:
    for product in all_products:
        if (product.id is None) or (user.id is None):
            raise NoneIdException()
        yield Purchase(
            None,
            product.id,
            user.id,
            datetime.fromtimestamp(
                _faker.unix_time(
                    start_datetime=date(2022, 1, 1),
                )
            )
        )

def gen_all_gifts(
    purchases: List[Purchase],
    recipient: User,
) -> Iterable[Gift]:
    for purchase in purchases:
        if (purchase.id is None) or (recipient.id is None):
            raise NoneIdException()
        yield Gift(
            None,
            purchase.id,
            recipient.id,
            _faker.emoji(),
            _faker.text()
        )


def gen_2_users() -> Iterable[User]:
    for _ in range(2):
        yield User(
            id = None,
            email = _faker.ascii_email(),
            password = _faker.password(),
            username = _faker.user_name(),
            money = _faker.pydecimal(max_value=10000, positive=True, right_digits=2),
            publisher_id = None
        )
