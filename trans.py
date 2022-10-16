#encoding: utf-8

from string import ascii_uppercase

class VarPlanner:

	class CannotGet(Exception): ...
	class ForeignElement(Exception): ...
	class UnalocatedElement(Exception): ...

	def __init__(self, name: str, space: list[str]):

		self._name: str = name
		self._space: list[str] = space
		self._allocated: set[str] = set()

	def get(self) -> str:
		"""returns an available element"""

		for e in self._space:
			if e not in self._allocated:
				return e

		raise self.CannotGet(f"{self._name} cannot find an available element")

	def alloc(self, e: str):
		"""marks an element as unavailable"""

		if e not in self._space:
			raise self.ForeignElement(f"{e} is not in the space of {self._name} and therefore cannot be allocated by it")

		self._allocated.add(e)

	def free(self, e: str):
		"""marks an element as available"""

		if e not in self._space:
			raise self.ForeignElement(f"{e} is not in the space of {self._name} and therefore cannot be freed from it")
		
		try:
			self._allocated.remove(e)

		except KeyError as e:
			raise self.UnalocatedElement(f"{e} is not allocated in {self._name} and therefore cannot be freed from it") from e

class TargetCode:

	def __init__(self):

		self._lines: list[str] = []

	def write_ln(self, txt: str):
		self._lines.append(txt)

	def compute_output(self) -> str:
		return ":".join(self._lines)

class BaseLocator:

	def __init__(self):

		self.small_vars = VarPlanner("small vars", list(ascii_uppercase))
		self.med_vars = VarPlanner("med vars", list(str(n) for n in range(1, 999 + 1)))
		self.target_code = TargetCode()

Locator = BaseLocator()

class Var:

	@property
	def addr(self) -> str: ...

	@property
	def val(self) -> str: ...

	def __str__(self) -> str:
		return self.val

class Const(Var):

	class NoAddr(Exception): ...

	def __init__(self, val: str):

		self._val = val

	@property
	def addr(self) -> str:
		raise self.NoAddr

	@property
	def val(self) -> str:
		return self._val

class SmallVar(Var):

	class NoAddr(Exception): ...

	def __init__(self, init_val: str = None):

		self._val = Locator.small_vars.get()
		Locator.small_vars.alloc(self._val)

		if init_val is not None:

	@property
	def addr(self) -> str:
		raise self.NoAddr

	@property
	def val(self) -> str:
		return self._val
