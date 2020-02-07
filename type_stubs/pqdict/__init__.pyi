from typing import Generic, Iterable, List, Tuple, TypeVar, Union


_KT = TypeVar('_KT') # key type
_DT = TypeVar('_DT') # data type


class pqdict(Generic[KeyType, DataType]):
    def __init__(self, data: Iterable[DataType]=..., key: Iterable[KeyType]=..., reverse: bool=...) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __contains__(self, key: KeyType) -> bool:
        ...

    def __delitem__(self, key: KeyType) -> None:
        ...

    def additem(self, key: KeyType, value: DataType) -> None:
        ...

    def popitem(self) -> Tuple[KeyType, DataType]:
        ...

    def updateitem(self, key: KeyType, value: DataType) -> None:
        ...
