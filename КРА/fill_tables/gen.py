from typing import List, Iterable
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


def gen_reviews(
    products: List[Product], 
    users: List[User]
) -> Iterable[Review]:
    for product in products:
        for writer in rchoices(users, k=_faker.pyint(25, len(users))):
            if (product.id is None) or (writer.id is None):
                raise NoneIdException()
            yield Review(
                None,
                product.id,
                writer.id,
                _faker.text(),
                _faker.pyint(1,5),
                datetime.fromtimestamp(
                    _faker.unix_time(
                        start_datetime=date(2022, 1, 1),
                    )
                )
            )


def gen_gifts(
    purchases: List[Purchase],
    recipients: List[User],
    n: PositiveInt,
) -> Iterable[Gift]:
    for recipient in rchoices(recipients, k=n):
        purchase = rchoices(purchases, k=1)[0]
        while purchase.buyer_id == recipient:
            purchase = rchoices(purchases, k=1)[0]            
        if (purchase.id is None) or (recipient.id is None):
            raise NoneIdException()
        yield Gift(
            None,
            purchase.id,
            recipient.id,
            _faker.emoji(),
            _faker.text()
        )


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
    all_users: List[User],
    max_products_per_user: PositiveInt
) -> Iterable[Purchase]:
    for user in all_users:
        products_per_user = randint(1, max_products_per_user)
        for product in rchoices(all_products, k=products_per_user):
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


@lru_cache()
def gen_tags() -> Iterable[Tag]:
    # return tags
    html_text = requests.get(
        'https://store.steampowered.com/tag/browse/#global_492'
        ).text
    html = BeautifulSoup(html_text, "lxml")
    return map(
        lambda x: Tag(x[0], x[1].text), # type: ignore
        enumerate(html.select('.tag_browse_tag'))
    )


def gen_assigned_tags(
    tags: List[Tag],
    products: List[Product],
    max_tags_per_product: PositiveInt
) -> Iterable[AssignedTag]:
    for p in rsample(products, k=len(products)):
        for t in rsample(tags, k=randint(1, max_tags_per_product)):
            if (t.id is None) or (p.id is None):
                raise Exception('id is None in gen')
            yield AssignedTag(t.id, p.id)


def gen_users(publishers: List[Publisher], n: PositiveInt) -> Iterable[User]:
    if n < len(publishers):
        raise Exception("not enough users for publishers")
    with_publishers = rsample(range(n), k=len(publishers))
    
    publisherIndex = 0
    for i in range(n):
        publisher_id = None
        if i in with_publishers:
            publisher_id = publishers[publisherIndex].id
            if publisher_id is None:
                raise NoneIdException()
            publisherIndex += 1
        yield User(
            id = None,
            email = _faker.ascii_email(),
            password = _faker.password(),
            username = _faker.user_name(),
            money = _faker.pydecimal(max_value=10000, positive=True, right_digits=2),
            publisher_id = publisher_id
        )


def gen_dependencies(
    products: List[Product],
    max_dlc_per_game: PositiveInt
) -> Iterable[ProductDependency]:
    used = []
    for required in rchoices(products, k=len(products)):
        used.append(required)
        for requested in rchoices(products, k=max_dlc_per_game):
            if requested in used:
                continue
            used.append(requested)
            yield ProductDependency(
                requested.id,
                required.id
            )
