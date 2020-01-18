from typing import Generic, Iterator, List, Tuple, TypeVar, Union


DataType = TypeVar('DataType')


class Item(Generic[DataType]):
	@property
	def key(self) -> str:
		...

	@property
	def value(self) -> float:
		...

	@property
	def data(self) -> DataType:
		...

	def __eq__(self, other: Any) -> bool:
		...

	def __ne__(self, other: Any) -> bool:
		...



class KeyedPQ(Generic[DataType]):
	def __init__(self, max_heap: bool=False) -> None:
		...

	def __len__(self) -> int:
		...

	def __contains__(self, identifier: Union[str, Item[DataType]]) -> bool:
		...

	def __getitem__(self, identifier: Union[str, Item[DataType]]) -> Item[DataType]:
		...

	def __delitem__(self, identifier: Union[str, Item[DataType]]) -> None:
		...

	def add(self, key: str, value: float, data: DataType) -> Item[DataType]:
		...

	def change_value(self, identifier: Union[str, Item[DataType]], value: float) -> Item[DataType]:
		...

	def add_or_change_value(self, key: str, value: float, data: DataType) -> Item[DataType]:
		...

	def peek(self) -> Item[DataType]:
		...

	def pop(self) -> Tuple[str, float, DataType]:
		...

	def ordered_iter(self) -> Iterator[Item[DataType]]:
		...

	def _export(self) -> List[float]:
		...

	def _verify_invariants(self) -> bool:
		...
