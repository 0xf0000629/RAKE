from op_lib import opcode, opcode_dict
from typing import List, Union, Dict
import sys, json


class IOUnit:
    def __init__(iounit, input, output):
        iounit.ibuffer = input
        iounit.ihead = 0
        iounit.obuffer = output

    def latch(iounit):
        iounit.ihead+=1

    def read(iounit):
        if iounit.ihead != len(iounit.ibuffer):
            return iounit.ibuffer[iounit.ihead]
        else:
            return None
    
    def write(iounit, val):
        iounit.obuffer.append(val)





class Memory:
    def __init__(memory, data):
        memory.array = data
        memory.address = 0

    def latch(memory, id):
        if id >= 0:
            memory.address = id
        else:
            memory.address += 1
    
    def load(memory):
        return memory.array[memory.address]
    
    def save(memory, value):
        memory.array[memory.address] = value

class DataPath:
    def __init__(dp, size, iounit):
        dp.stacksize = size
        dp.stack = [0] * size
        dp.callstacksize = size
        dp.callstack = [0] * size
        dp.io = iounit
        dp.datapointer = 0
        dp.callpointer = 0
        dp.alu = 0
    
    def latch_pointer(dp, pos):
        dp.datapointer += pos
    
    def latch_callpointer(dp, pos):
        dp.callpointer += pos
    
    def get_tos(dp, pos):
        return dp.stack[dp.datapointer-pos]
    
    def push_data(dp, val):
        dp.stack[dp.datapointer] = val
        dp.latch_pointer(1)
    
    def pop_data(dp):
        dp.stack[dp.datapointer-1] = 0
        dp.latch_pointer(-1)

    def push_call(dp, val):
        dp.callstack[dp.callpointer] = val
        dp.latch_callpointer(1)
    
    def pop_call(dp):
        dp.alu = dp.callstack[dp.callpointer-1]
        dp.latch_callpointer(-1)
    
    def latch_binary(dp, operation):
        if operation == opcode.ADD:
            dp.alu = dp.get_tos(2) + dp.get_tos(1)
            dp.latch_pointer(-2)
        elif operation == opcode.SUB:
            dp.alu = dp.get_tos(2) - dp.get_tos(1)
            dp.latch_pointer(-2)
        elif operation == opcode.MLT:
            dp.alu = dp.get_tos(2) * dp.get_tos(1)
            dp.latch_pointer(-2)
        elif operation == opcode.DIV:
            dp.alu = dp.get_tos(2) / dp.get_tos(1)
            dp.latch_pointer(-2)
        elif operation == opcode.MOD:
            dp.alu = dp.get_tos(2) % dp.get_tos(1)
            dp.latch_pointer(-2)
        elif operation == opcode.EQL:
            dp.alu = dp.get_tos(2) == dp.get_tos(1)
        elif operation == opcode.GRT:
            dp.alu = dp.get_tos(2) > dp.get_tos(1)
        elif operation == opcode.LST:
            dp.alu = dp.get_tos(2) < dp.get_tos(1)
        elif operation == opcode.INC:
            dp.alu = dp.get_tos(1)+1
            dp.latch_pointer(-1)
        elif operation == opcode.DEC:
            dp.alu = dp.get_tos(1)-1
            dp.latch_pointer(-1)
    
    def input_data(dp):
        dp.alu = dp.io.read()
        dp.io.latch()
    
    def output_data(dp, val):
        dp.io.write(val)

class ControlUnit:
    def __init__(CU, dpath, mem):
        CU.datapath = dpath
        CU.memory = mem
        CU.ipointer = 0
        CU.running = 1
        CU.ticks = 0
    
    def latch(CU, shift):
        if shift == None:
            CU.ipointer+=1
        else:
            CU.ipointer = shift
    
    def tick(CU):
        CU.ticks+=1
    
    def execute(CU):
        CU.memory.latch(CU.ipointer)
        instruction = CU.memory.load()
        if instruction["opcode"] == opcode.PUSH:
            CU.datapath.push_data(instruction["arg"])
            CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.LOAD:
            CU.memory.latch(CU.datapath.get_tos(1))
            CU.tick()
            CU.datapath.pop_data()
            CU.tick()
            CU.datapath.push_data(CU.memory.load())
            CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.SAVE:
            CU.memory.latch(instruction["arg"])
            CU.memory.save(CU.datapath.get_tos(1))
            CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.POP:
            CU.datapath.pop_data()
            CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.CALL:
            CU.datapath.push_call(CU.ipointer)
            CU.latch(instruction["arg"])
            CU.tick()
        elif instruction["opcode"] == opcode.RET:
            CU.datapath.pop_call()
            CU.tick()
            CU.latch(CU.datapath.alu)
            CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.JMP:
            CU.latch(instruction["arg"])
            CU.tick()
        elif instruction["opcode"] == opcode.JZ:
            if CU.datapath.alu == 0:
                CU.latch(instruction["arg"])
                CU.tick()
            else:
                CU.latch(None)
                CU.tick()
        elif instruction["opcode"] == opcode.IN:
            CU.datapath.input_data()
            CU.tick()
            CU.datapath.push_data(CU.datapath.alu)
            if CU.datapath.alu == None:
                CU.running = 0    
            else:
                CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.OUT:
            CU.datapath.alu = CU.datapath.get_tos(1)
            CU.tick()
            CU.datapath.io.write(CU.datapath.alu)
            CU.latch(None)
            CU.tick()
        elif instruction["opcode"] == opcode.PRINT:
            CU.memory.latch(instruction["arg"])
            CU.datapath.alu = CU.memory.load()
            CU.tick()
            while CU.datapath.alu != 0:
                CU.datapath.io.write(CU.datapath.alu)
                CU.tick()
                CU.memory.latch(-1)
                CU.datapath.alu = CU.memory.load()
                CU.tick()
            CU.latch(None)
        elif instruction["opcode"] == opcode.HLT:
            CU.running = 0
        else:
            CU.datapath.latch_binary(instruction["opcode"])
            CU.tick()
            if instruction["opcode"] not in [opcode.GRT, opcode.LST, opcode.EQL, opcode.NONE]:
                CU.datapath.push_data(CU.datapath.alu)
            CU.tick()
            CU.latch(None)
        


def simulate(code, limit, input):
    output = []
    iounit = IOUnit(input, output)
    mem = Memory(code)
    dpath = DataPath(1000, iounit)

    logs = []
    control_unit = ControlUnit(dpath, mem)

    while control_unit.ipointer < limit:
        control_unit.execute()
        if control_unit.running == 1: 
            logs.append(dict(
                    ip=control_unit.ipointer, 
                    tick=control_unit.ticks, 
                    sp=control_unit.datapath.datapointer, 
                    cp=control_unit.datapath.callpointer, 
                    alu=control_unit.datapath.alu, 
                    instr=code[control_unit.ipointer]["opcode"],
                    term=code[control_unit.ipointer]["source"]
            ))
        else:
            break

    return logs, output

if __name__ == "__main__":
    assert len(sys.argv) == 4, "Usage: stack_machine.py <input_file> <code_file> <log_file>"
    myself, data_input, code_input, log_output = sys.argv
    ifile = open(data_input, "r", encoding="utf-8")
    cfile = open(code_input, "r", encoding="utf-8")
    lfile = open(log_output, "w", encoding="utf-8")
    data = json.loads(cfile.read())
    icode: List[Union[Dict, int]] = []
    for i in range(250):
        icode.append(dict())
    for i in range(750):
        icode.append(0)
    for i in range(len(data)):
        icode[data[i]["index"]] = data[i]["value"]
    inp = ifile.read().split(' ')
    result = simulate(icode, 200, inp)
    outp = result[1]
    logs = []
    for i in range(len(result[0])):
        logs.append(json.dumps(result[0][i]))
    lfile.write("[" + ",\n".join(logs) + "]")
    lfile.write("\nOutput: " + "".join(str(x)+'' for x in outp))







    


    


