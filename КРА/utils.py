from typing import List, Annotated, TypeAlias, Iterable, TypeVar
from annotated_types import Gt
from faker import Faker

PositiveInt: TypeAlias = Annotated[int, Gt(0)]
_faker = Faker()

T = TypeVar('T')
def get_rands_from_list(l: List[T], max_count = None) -> List[T]:
    if max_count is None:
        max_count = len(l)
    count = _faker.pyint(1, max_count)
    return [l[_faker.pyint(0, len(l)-1)] for _ in range(count)]
