from typing import Generic, List, Tuple, TypeVar, Union


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


class AddressablePQ(Generic[DataType]):
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

	def change_value(self, identifier: Union[str, Item[DataType]], value: float) -> None:
		...

	def add_or_change(self, key: str, value: float, data: DataType) -> Item[DataType]:
		...

	def peek(self) -> Item[DataType]:
		...

	def pop(self) -> Tuple[str, float, DataType]:
		...

	def _export(self) -> List[float]:
		...

	def _verify_invariants(self) -> bool:
		...
