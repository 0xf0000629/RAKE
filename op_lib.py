from enum import Enum

class opcode(str, Enum):
    PUSH = "push"
    POP = "pop"

    LOAD = "load"
    SAVE = "save"

    IN = "input"
    OUT = "output"
    PRINT = "print"

    NONE = "none"
    HLT = "halt"

    CALL = "call"
    RET = "ret"

    JMP = "jump"
    JZ = "jumpzero"

    ADD = "add"
    SUB = "sub"
    MLT = "mult"
    DIV = "div"
    MOD = "mod"
    GRT = "grt"
    LST = "lst"
    EQL = "equal"
    INC = "inc"
    DEC = "dec"


opcode_dict = {
    "+": opcode.ADD,
    "-": opcode.SUB,
    "*": opcode.MLT,
    "/": opcode.DIV,
    "%": opcode.MOD,
    ">": opcode.GRT,
    "<": opcode.LST,
    "==": opcode.EQL,
    ".": opcode.OUT,
    "!": opcode.LOAD,
    "in": opcode.IN,
    "drop": opcode.POP,
    "halt": opcode.HLT
}