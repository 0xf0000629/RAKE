from stack_machine import *
from translator import *
import sys

def simulate(code, limit, input):
    output = []
    iounit = IOUnit(input, output)
    mem = Memory(code)
    dpath = DataPath(1000, iounit)

    control_unit = ControlUnit(dpath, mem)

    while control_unit.ipointer < limit:
        control_unit.execute()
        if control_unit.running == 0: break

    return control_unit.datapath.io.obuffer



assert len(sys.argv) == 3, "Usage: rake.py <input_file> <target_file>"
myself, input, output = sys.argv
code = translate(input, output)
outp = simulate(code, 200, [])
print("".join(str(x) for x in outp))
