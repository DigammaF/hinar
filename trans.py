#encoding: utf-8

from __future__ import annotations
from enum import Enum
from io import TextIOWrapper
from math import gcd

from string import ascii_uppercase
from typing import Any, Protocol, Tuple, Union

ASS = "→"
L = "⌊"

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

	def alloc(self, e: str) -> str:
		"""marks an element as unavailable"""

		if e not in self._space:
			raise self.ForeignElement(f"{e} is not in the space of {self._name} and therefore cannot be allocated by it")

		self._allocated.add(e)
		return e

	def get_allocated(self) -> str:
		"""returns an allocated element"""
		return self.alloc(self.get())

	def free(self, e: str):
		"""marks an element as available"""

		if e not in self._space:
			raise self.ForeignElement(f"{e} is not in the space of {self._name} and therefore cannot be freed from it")
		
		try:
			self._allocated.remove(e)

		except KeyError as err:
			raise self.UnalocatedElement(f"{e} is not allocated in {self._name} and therefore cannot be freed from it") from err

class TargetCode:

	def __init__(self):

		self._lines: list[str] = []

	def write_ln(self, txt: str):
		self._lines.append(txt)

	def compute_output(self) -> str:
		return "\n".join(self._lines)

	def output(self, file: TextIOWrapper):
		file.write(self.compute_output())

class BaseLocator:

	def __init__(self):

		self.small_vars = VarPlanner("small vars", list(ascii_uppercase))
		self.med_vars = VarPlanner("med vars", list(str(n) for n in range(1, 999 + 1)))
		self.string_vars = VarPlanner("string vars", list(f"Chn{str(n)}" for n in range(9 + 1)))
		self.target_code = TargetCode()

Locator = BaseLocator()

class BaseVar: ...

class String(BaseVar):

	def __init__(self) -> None:

		self._val: str = Locator.string_vars.get()
		Locator.string_vars.alloc(self._val)

	def __str__(self) -> str:
		return self._val

	@property
	def val(self) -> str:
		return self._val

class StringConst(BaseVar):

	def __init__(self, text: str):

		self._text = text

	def __str__(self) -> str:
		return self.val

	@property
	def val(self) -> str:
		return '"' + self._text + '"'

class Var(BaseVar):

	@property
	def addr(self) -> str: ...

	@property
	def val(self) -> str: ...

	def __str__(self) -> str:
		return self.val

	def set(self, val: NumVal):
		Locator.target_code.write_ln(f"{get_num_val(val)}→{self.val}")

	def incr(self):
		self.set(self + Const(1))

	def decr(self):
		self.set(self - Const(1))

	def simplified(self, ctx: list[NumOp]) -> NumVal:
		return self

	def __add__(self, other) -> Paren:
		return Paren(Addition(self, other))

	def __sub__(self, other) -> Paren:
		return Paren(Substraction(self, other))

	def __mul__(self, other) -> Paren:
		return Paren(Multiplication(self, other))

	def __truediv__(self, other) -> Paren:
		return Paren(Division(self, other))

	def __eq__(self, other) -> Paren:
		return Paren(BinLogicOp("=", self, other))

	def __neq__(self, other) -> Paren:
		return Paren(BinLogicOp("≠", self, other))

	def __gt__(self, other) -> Paren:
		return Paren(BinLogicOp(">", self, other))

	def __ge__(self, other) -> Paren:
		return Paren(BinLogicOp("≥", self, other))

	def __lt__(self, other) -> Paren:
		return Paren(BinLogicOp("<", self, other))

	def __le__(self, other) -> Paren:
		return Paren(BinLogicOp("≤", self, other))

	def __and__(self, other) -> Paren:
		return Paren(BinLogicOp(" et ", self, other))

	def __or__(self, other) -> Paren:
		return Paren(BinLogicOp(" ou ", self, other))

	def __invert__(self) -> Not:
		return Not(self)

class RefTypeUnit(Enum):

	no_ref = "no ref"
	med_var = "med var"
	struct_instance = "struct instance"

RefType = Tuple[RefTypeUnit]

def read_ref_type(expr: NumVal) -> RefType:

	if isinstance(expr, (SmallVar, MedVar)):
		return expr.ref_type

	else:
		return (RefTypeUnit.no_ref,)

class CannotDeref(Exception): ...

def deref(var: Var) -> Union[MedVar, Struct]:

	ref_type = read_ref_type(var)

	if ref_type[-1] == RefTypeUnit.med_var:
		return MedVar(addr=var.val)

	elif ref_type[-1] == RefTypeUnit.struct_instance:

		addr_bearer = SmallVar()
		addr_bearer.set(var.val)
		return Struct(addr=addr_bearer.val) # the val will be used as a SmallVar addr

	else:
		raise CannotDeref(f"Cannot dereference an expression with reference type {ref_type}")

NumVal = Union[Var, "NumOp"]

class NumOp:
	
	def simplified(self, ctx: list[NumOp]) -> NumVal: ...
	
	def __str__(self) -> str:
		return self.val

	@property
	def val(self) -> str: ...

	def __add__(self, other) -> Paren:
		return Paren(Addition(self, other))

	def __sub__(self, other) -> Paren:
		return Paren(Substraction(self, other))

	def __mul__(self, other) -> Paren:
		return Paren(Multiplication(self, other))

	def __truediv__(self, other) -> Paren:
		return Paren(Division(self, other))

	def __eq__(self, other) -> Paren:
		return Paren(BinLogicOp("=", self, other))

	def __neq__(self, other) -> Paren:
		return Paren(BinLogicOp("≠", self, other))

	def __gt__(self, other) -> Paren:
		return Paren(BinLogicOp(">", self, other))

	def __ge__(self, other) -> Paren:
		return Paren(BinLogicOp("≥", self, other))

	def __lt__(self, other) -> Paren:
		return Paren(BinLogicOp("<", self, other))

	def __le__(self, other) -> Paren:
		return Paren(BinLogicOp("≤", self, other))

	def __and__(self, other) -> Paren:
		return Paren(BinLogicOp(" et ", self, other))

	def __or__(self, other) -> Paren:
		return Paren(BinLogicOp(" ou ", self, other))

	def __invert__(self) -> Not:
		return Not(self)

class ExprRoot(NumOp):

	def __init__(self, a: NumVal):

		self._a: NumVal = a

	def simplified_root(self) -> NumVal:
		return self._a if isinstance(self._a, Var) else self._a.simplified([self])

class Paren(NumOp):

	def __init__(self, a: NumVal):

		self._a: NumVal = a

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])

		if isinstance(a, Var):
			return a

		if isinstance(ctx[-1], Paren):
			return a.simplified(ctx)

		elif isinstance(a, (Multiplication, Division)) and isinstance(ctx[-1], (Addition, Substraction)):
			return a.simplified(ctx)

		elif isinstance(a, (Addition, Substraction)) and isinstance(ctx[-1], (Addition, Substraction)) or isinstance(a, (Multiplication, Division)) and isinstance(ctx[-1], (Multiplication, Division)):
			return a.simplified(ctx)

		else:
			return a.simplified(ctx) if isinstance(ctx[-1], ExprRoot) else Paren(a.simplified(ctx + [self]))

	@property
	def val(self) -> str:
		return f"({self._a.val})"

def pa(expr: NumVal) -> Paren:
	return Paren(expr)

class BinLogicOp(NumOp):

	def __init__(self, ti_sym: str, a: NumVal, b: NumVal):

		self._ti_sym: str = ti_sym
		self._a = a
		self._b = b

	@property
	def val(self) -> str:
		return f"{get_num_val(self._a)}{self._ti_sym}{get_num_val(self._b)}"

	def simplified(self, ctx: list[NumOp]) -> NumVal:
		return BinLogicOp(self._ti_sym, self._a.simplified(ctx + [self]), self._b.simplified(ctx + [self]))

class Neg(NumOp):

	def __init__(self, a: NumVal):

		self._a: NumVal = a

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])

		if isinstance(a, Neg):
			
			child = a.child
			return child if isinstance(child, Var) else child.simplified(ctx)

		return Neg(a)

	@property
	def child(self) -> NumVal:
		return self._a

	@property
	def val(self) -> str:
		return f"0-{self._a}"

class Not(NumOp):

	def __init__(self, a: NumVal):

		self._a: NumVal = a

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])

		if isinstance(a, Not):
			
			child = a.child
			return child if isinstance(child, Var) else child.simplified(ctx)

		return Not(a)

	@property
	def child(self) -> NumVal:
		return self._a

	@property
	def val(self) -> str:
		return f"non({self._a})"

class Addition(NumOp):

	def __init__(self, a: NumVal, b: NumVal):

		self._a = a
		self._b = b

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])
		b = self._b.simplified(ctx + [self])

		if a.val == "0": return b
		if b.val == "0": return a

		if isinstance(a, Const) and isinstance(b, Const):
			return Const(eval(f"{a} + {b}"))

		return Addition(a, b)

	@property
	def val(self) -> str:
		return f"{self._a}+{self._b}"

class Substraction(NumOp):

	def __init__(self, a: NumVal, b: NumVal):

		self._a = a
		self._b = b

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])
		b = self._b.simplified(ctx + [self])

		if a.val == "0": return Neg(b).simplified(ctx)
		if b.val == "0": return a

		if isinstance(a, Const) and isinstance(b, Const):
			return Const(eval(f"{a} - {b}"))

		return Substraction(a, b)

	@property
	def val(self) -> str:
		return f"{self._a}-{self._b}"

class Multiplication(NumOp):

	def __init__(self, a: NumVal, b: NumVal):

		self._a = a
		self._b = b

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])
		b = self._b.simplified(ctx + [self])

		if a.val == "0" or b.val == "0": return Const("0")
		if a.val == "1": return b
		if b.val == "1": return a

		if isinstance(a, Const) and isinstance(b, Const):
			return Const(eval(f"{a} * {b}"))

		return Multiplication(a, b)

	@property
	def val(self) -> str:
		return f"{self._a}*{self._b}"

class Division(NumOp):

	def __init__(self, a: NumVal, b: NumVal):

		self._a = a
		self._b = b

	def simplified(self, ctx: list[NumOp]) -> NumVal:

		a = self._a.simplified(ctx + [self])
		b = self._b.simplified(ctx + [self])

		if b.val == "0": raise ValueError("cannot divide by zero!")

		if a.val == "0": return Const("0")
		if b.val == "1": return a

		if isinstance(a, Const) and isinstance(b, Const):

			af, bf = float(a.val), float(b.val)
			num, den = (af/bf).as_integer_ratio()

			if af.is_integer() and bf.is_integer():
				if (n := gcd(int(af), int(bf))) > 1:
					return Division(Const(int(af/n)), Const(int(bf/n)))

			elif max(num, den) < 100:
				return Division(Const(num), Const(den))

		return Division(a, b)

	@property
	def val(self) -> str:
		return f"{self._a}/{self._b}"

def get_num_val(expr: NumVal) -> str:
	return ExprRoot(expr).simplified_root().val

class Const(Var):

	class NoAddr(Exception): ...

	def __init__(self, val: Any):

		if type(val) is str:
			self._val: str = val

		else:
			self._val: str = str(val)

	@property
	def addr(self) -> str:
		raise self.NoAddr

	@property
	def val(self) -> str:
		return self._val

class NumRaw(Var):

	class NoAddr(Exception): ...

	def __init__(self, text: str):

		self._text = text

	@property
	def addr(self) -> str:
		raise self.NoAddr

	@property
	def val(self) -> str:
		return self._text

class SmallVar(Var):

	def __init__(self, init_val: str = None, ref_type: RefType = (RefTypeUnit.no_ref,)):

		self._ref_type: RefType = ref_type
		self._addr: str = Locator.small_vars.get()
		Locator.small_vars.alloc(self._addr)

		if init_val is not None:
			self.set(NumRaw(init_val))

	@property
	def ref_type(self) -> RefType:
		return self._ref_type

	@property
	def addr(self) -> str:
		return self._addr

	@property
	def val(self) -> str:
		return self._addr

	def __del__(self):
		Locator.small_vars.free(self._addr)

	def clone(self) -> SmallVar:
		return SmallVar(init_val=self.val, ref_type=self._ref_type)

class MedVar(Var):

	def __init__(self, init_val: str = "0", addr: str or None = None, ref_type: RefType = (RefTypeUnit.no_ref,)):

		self._ref_type: RefType = ref_type

		if addr is None:
			self._addr: str = Locator.med_vars.get_allocated()
			self.set(NumRaw(init_val))

		else:
			self._addr: str = addr

	@property
	def ref_type(self) -> RefType:
		return self._ref_type

	@property
	def addr(self) -> str:
		return self._addr

	@property
	def val(self) -> str:
		return f"⌊RAM({self._addr})"

	def __del__(self):

		if self._ref_type == (RefTypeUnit.no_ref,):
			Locator.med_vars.free(self._addr)

	def ref(self) -> MedVar:
		return MedVar(self._addr, ref_type=self._ref_type + (RefTypeUnit.med_var,))

	def small_ref(self) -> SmallVar:
		return SmallVar(self._addr, ref_type=self._ref_type + (RefTypeUnit.med_var,))

	def clone(self) -> MedVar:
		return MedVar(init_val=self.val, ref_type=self._ref_type)

class StructMember(Var):

	def __init__(self, struct_addr: str, index: str):

		self._struct_addr: str = struct_addr
		self._index: str = index

	@property
	def addr(self) -> str:
		return f"(⌊ADR({self._struct_addr})+{self._index})"

	@property
	def val(self) -> str:
		return f"⌊DAT{self.addr}"

def defrag_mem():
	Locator.target_code.write_ln("prgmHNDEFRAG")

def init_mem():
	Locator.target_code.write_ln("prgmHNINIT")

class Struct(Var):

	class CannotFindMember(Exception): ...

	def __init__(self, init_vals: tuple[tuple[str, NumVal]] = None, addr: str or None = None):

		if init_vals is None: init_vals = {}

		if addr is None:

			self._addr = SmallVar()
			Locator.target_code.write_ln("{" + ",".join(ExprRoot(v).simplified_root().val for v in init_vals.values()))
			Locator.target_code.write_ln("prgmHNALLOC")
			self._addr.set(NumRaw("Rep"))

		else:

			self._addr = SmallVar(addr)

		self._members: tuple[tuple[str, StructMember]] = tuple((k, StructMember(self._addr.val, str(n))) for n, (k, _) in enumerate(init_vals))

	def clone(self) -> Struct:

		clone = Struct({k: Const(0) for k in self._members})

		with For(..., Const(0), Const(len(self._members) - 1)) as fl:
			StructMember(clone.addr, fl.var.val).set(StructMember(self.addr, fl.var.val))

		return clone

	def get_member(self, name: str) -> StructMember:
		
		for lname, member in self._members:
			if lname == name:
				return member

		raise self.CannotFindMember(name)

	@property
	def addr(self) -> str:
		return self._addr.val

	@property
	def val(self) -> str:
		return f"⌊DAT{self.addr}"

	def __del__(self):
		Locator.target_code.write_ln(f"0{ASS}⌊ADR({self._addr.val})")
		del self._addr

	def ref(self) -> MedVar:
		return MedVar(self._addr.val, ref_type=(RefTypeUnit.no_ref, RefTypeUnit.struct_instance))

	def small_ref(self) -> SmallVar:
		return SmallVar(self._addr.val, ref_type=(RefTypeUnit.no_ref, RefTypeUnit.struct_instance))

def wraw(text: str):
	Locator.target_code.write_ln(text)

class ControlFlow:

	@property
	def introduction(self) -> str: ...
	@property
	def sanction(self) -> str: ...

	def __enter__(self) -> ControlFlow:
		Locator.target_code.write_ln(self.introduction)
		return self

	def __exit__(self, *args, **kwargs):
		Locator.target_code.write_ln(self.sanction)

class While(ControlFlow):

	def __init__(self, condition: NumVal):

		self._condition: NumVal = condition

	@property
	def introduction(self) -> str:
		return f"While {ExprRoot(self._condition).simplified_root().val}"

	@property
	def sanction(self) -> str:
		return "End"

def Range(size: NumVal) -> Tuple[NumVal, NumVal]:
	return Const(0), size

def Amount(n: NumVal) -> Tuple[NumVal, NumVal]:
	return Const(1), n

class For(ControlFlow):

	def __init__(self, svar: SmallVar or Ellipsis, start_: NumVal, end_: NumVal, step: NumVal = None):

		if svar is Ellipsis:
			self._is_temp = True
			svar = SmallVar()

		else:
			self._is_temp = False

		self._svar: SmallVar = svar
		self._start: NumVal = start_
		self._end: NumVal = end_
		self._step: NumVal or None = step

	def __enter__(self) -> For:
		Locator.target_code.write_ln(self.introduction)
		return self

	@property
	def var(self) -> SmallVar:
		return self._svar

	@property
	def introduction(self) -> str:
		return f"For({self._svar.val},{get_num_val(self._start)},{get_num_val(self._end)}" + (f",{get_num_val(self._step)}" if self._step is not None else "")

	@property
	def sanction(self) -> str:

		if self._is_temp:
			del self._svar

		return "End"

	def Break(self):

		self._svar.set(self._end + Const(1))

def Else():
	wraw("Else")

class If(ControlFlow):

	def __init__(self, condition: NumVal):

		self._condition: NumVal = condition

	@property
	def introduction(self) -> str:
		return f"If {ExprRoot(self._condition).simplified_root().val}: Then"

	@property
	def sanction(self) -> str:
		return "End"

def Disp(var: NumVal or String or StringConst):
	wraw("Disp " + get_num_val(var))

def Input(prompt: String or StringConst, var: Var or String):
	wraw(f"Input {prompt.val},{var.val}")

true = Const(1)
false = Const(0)

class Array(Var):

	class NoVal(Exception): ...

	def __init__(self, size: NumVal, ref_type: RefType = (RefTypeUnit.no_ref,), _init: bool = True):

		self._size: NumVal = size
		self._ref_type: RefType = ref_type
		self._lsize: int = eval(get_num_val(size))
		self._addrs: list[str] = [Locator.med_vars.get_allocated() for _ in range(self._lsize)]

		if _init:
			with For(..., Const(1), Const(self._lsize)) as forloop:
				wraw(f"0{ASS}⌊RAM({forloop.var.val}")

	@property
	def addr(self) -> str:
		return self._addrs[0]

	@property
	def val(self) -> str:
		raise self.NoVal

	def __getitem__(self, key: NumVal) -> MedVar:
		return MedVar(addr=get_num_val(Const(self.addr) + key), ref_type=self._ref_type)

	def __del__(self):

		for addr in self._addrs:
			Locator.med_vars.free(addr)

	def clone(self) -> Array:

		clone = Array(self._size, self._ref_type, _init=False)

		with For(..., Const(1), Const(self._lsize)) as fl:
			clone[fl.var.val].set(self[fl.var.val])

		return clone
