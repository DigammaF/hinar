
from trans import *

def int_part(x: NumVal) -> NumRaw:
	return NumRaw(f"partEnt({get_num_val(x)})")

amount = SmallVar()
Input(StringConst("Quantité de nombres premiers à générer; "), amount)
n = SmallVar(2)

with While(amount):

	is_prime = SmallVar(true)

	with For(..., Const(2), n) as forloop:

		with If(int_part(n/forloop.var) == Const(0)):

			is_prime.set(false)
			forloop.Break()

	with If(is_prime):

		amount.decr()
		Disp(n)

	n.incr()

Locator.target_code.output(open("primes.txt", "w", encoding="utf-8"))
