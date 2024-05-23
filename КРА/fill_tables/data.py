from typing import ClassVar, Optional
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass


class Data:
    table_name: ClassVar[str]


@dataclass
class Publisher(Data):
    id: Optional[int]
    name: str
    description: str
    bank_account: str

    table_name: ClassVar[str] = 'Publisher'


@dataclass
class User(Data):
    id: Optional[int]
    email: str
    password: str
    username: str
    money: Decimal
    publisher_id: int
    
    table_name: ClassVar[str] = '"User"'


@dataclass
class Tag(Data):
    id: Optional[int]
    name: str

    table_name: ClassVar[str] = 'Tag'


@dataclass
class Product(Data):
    id: Optional[int]
    name: str
    description: str
    price: Decimal
    publisher_id: int
    reviews_count: int
    rating_sum: int

    table_name: ClassVar[str] = 'Product'


@dataclass
class Gift(Data):
    id: Optional[int]
    purchase_id: int
    recipient_id: int
    title: str
    message: str
    
    table_name: ClassVar[str] = 'gift'


@dataclass
class AssignedTag(Data):
    tag_id: int
    product_id: int

    table_name: ClassVar[str] = 'AssignedTag'


@dataclass
class Purchase(Data):
    id: Optional[int]
    product_id: int
    buyer_id: int
    date: datetime

    table_name: ClassVar[str] = 'Purchase'


@dataclass
class Review(Data):
    id: Optional[int]
    subject_id: int
    writer_id: int
    text: str
    rating: int
    date: datetime

    table_name: ClassVar[str] = 'Review'


@dataclass
class ProductDependency(Data):
    primary_id: int
    dependant_id: int

    table_name: ClassVar[str] = 'ProductDependency'
