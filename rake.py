from stack_machine import *
from translator import *
import sys

assert len(sys.argv) == 3, "Usage: rake.py <input_file> <target_file>"
myself, input, output = sys.argv
code = translate(input, output)
outp = simulate(code, 200, [])
print("".join(str(x) for x in outp[1]))
