import re, json, sys
from op_lib import opcode, opcode_dict
        


def parse_all(data):
    data = data.replace('\n',' ').replace('\t',' ').split(' ')
    data = [str(i) for i in data if i != ""]

    it = 0
    while 1==1:
        if len(data[it]) >= 2 and data[it][0:2] == ".'":
            if data[it][-1] != "'":
                concat = data[it] + ' '
                del data[it]
                while data[it][-1] != "'":
                    concat += data[it] + ' '
                    del data[it]
                data[it] = concat+data[it]
        
        if data[it] == "loop":
            assert it >= 3, "missing arguments for 'loop'!"
            data[it] = "loop(" + data[it-3] + '|' + data[it-2] + '|' + data[it-1] + ")"
            del data[it-3], data[it-3], data[it-3]
            it -= 3
        it+=1
        if (it == len(data)):
            break

    code = [None] * 250 + [0] * 750
    for i in range(250):
        code[i] = dict()
    varpos = 250
    strpos = 500
    strings = dict()
    vars = dict()
    functions = dict()
    ifbuffer = []
    loopbuffer = []
    in_function = 0
    code[0]["opcode"] = opcode.JMP
    code_index = 1
    for i in range(len(data)):
        if data[i] == "if":
            code[code_index]["opcode"] = opcode.JZ
            ifbuffer.append({"if": code_index})
            code_index+=1
        elif data[i] == "else":
            code[code_index]["opcode"] = opcode.JMP
            ifbuffer[-1]["else"] = code_index
            code_index+=1
        elif data[i] == "then":
            code[code_index]["opcode"] = opcode.NONE
            ifbuffer[-1]["then"] = code_index
            code_index+=1
        elif data[i] == "ret":
            code[code_index]["opcode"] = opcode.RET
            code[code_index]["source"] = "ret"
            assert in_function == 1, "'ret' is not allowed outside of functions!"
            in_function = 0
            code_index+=1
        elif data[i] == "loopend":
            code[code_index]["opcode"] = opcode.PUSH
            code[code_index]["arg"] = loopbuffer[-1]["var"]
            code[code_index+1]["opcode"] = opcode.LOAD
            if loopbuffer[-1]["oper"] == "+":
                code[code_index+2]["opcode"] = opcode.INC
            else:
                code[code_index+2]["opcode"] = opcode.DEC
            code[code_index+3]["opcode"] = opcode.SAVE 
            code[code_index+3]["arg"] = loopbuffer[-1]["var"]
            code[code_index+4]["opcode"] = opcode.POP
            code[code_index+5]["opcode"] = opcode.JMP
            for k in range(code_index, code_index+6):
                code[k]["source"] = "loopend"
            loopbuffer[-1]["end"] = code_index+5
            code_index+=6
        else:
            if data[i] in opcode_dict:
                code[code_index]["opcode"] = opcode_dict[data[i]]
                code[code_index]["source"] = data[i]
                code_index+=1
            else:
                func_def_match = re.search(r"([A-Za-z_]+)\:", data[i])
                func_call_match = re.search(r"/([A-Za-z_]+)", data[i])
                num_match = re.search(r"([0-9]+)", data[i])
                str_match = re.search(r"\.'([\s\S]*)'", data[i])
                var_def_match = re.search(r"([A-Za-z_]+)=([0-9]+)", data[i])
                var_ass_match = re.search(r"=([A-Za-z_]+)", data[i])
                loop_match = re.search(r"loop\(([\s\S]*)\|([0-9]+)\|([+-])\)", data[i])
                if func_def_match != None:
                    func_name = func_def_match[1]
                    assert in_function == 0, "you can't define functions inside of functions or inside main code!"
                    assert func_name not in functions, "function " + func_name + " has already been defined!"
                    functions[func_name] = code_index
                    in_function = 1
                    continue
                elif in_function == 0:
                    code[0]["arg"] = code_index
                    in_function = -1
                if loop_match != None:
                    loopbuffer.append({"loop": code_index})
                    loop_var = loop_match[1]
                    loop_val = int(loop_match[2])
                    loop_oper = loop_match[3]
                    loopbuffer[-1]["oper"] = loop_oper
                    assert loop_var in vars, "variable " + loop_var + " has not been defined!"
                    loopbuffer[-1]["var"] = vars[loop_var]
                    code[code_index]["opcode"] = opcode.PUSH 
                    code[code_index]["arg"] = vars[loop_var]
                    code[code_index+1]["opcode"] = opcode.LOAD
                    code[code_index+2]["opcode"] = opcode.PUSH
                    code[code_index+2]["arg"] = loop_val
                    if loop_oper == "-":
                        code[code_index+3]["opcode"] = opcode.GRT
                    else:
                        code[code_index+3]["opcode"] = opcode.LST
                    code[code_index+4]["opcode"] = opcode.POP
                    code[code_index+5]["opcode"] = opcode.POP
                    code[code_index+6]["opcode"] = opcode.JZ
                    for k in range(code_index, code_index+7):
                        code[k]["source"] = loop_var + ' ' + str(loop_val) + ' ' + loop_oper + " loop"
                    loopbuffer[-1]["jump"] = code_index+6
                    code_index+=7
                elif str_match != None:
                    string = str_match[1]
                    if string not in strings:
                        strings[string] = strpos
                        code[code_index]["opcode"] = opcode.PRINT
                        code[code_index]["arg"] = strpos
                        code[code_index]["source"] = str_match.string
                        code_index+=1
                        for j in range(len(string)):
                            code[strpos] = string[j]
                            strpos+=1
                        code[strpos] = 0
                        strpos+=1
                    else:
                        code[code_index]["opcode"] = opcode.PRINT
                        code[code_index]["arg"] = strings[str]
                        code[code_index]["source"] = str_match.string
                        code_index+=1
                elif var_def_match != None:
                    varname = var_def_match[1]
                    value = int(var_def_match[2])
                    assert varname not in vars, "variable " + varname + " has already been defined!"
                    vars[varname] = varpos
                    code[varpos] = value
                    varpos+=1
                elif var_ass_match != None:
                    varname = var_ass_match[1]
                    assert varname in vars, "variable " + varname + "has not been defined!"
                    code[code_index]["opcode"] = opcode.SAVE
                    code[code_index]["arg"] = vars[varname]
                    code[code_index]["source"] = var_ass_match.string
                    code_index+=1
                elif func_call_match != None:
                    func_name = func_call_match[1]
                    assert func_name in functions, "function " + func_name + " has not been defined!"
                    code[code_index]["opcode"] = opcode.CALL
                    code[code_index]["arg"] = functions[func_name]
                    code[code_index]["source"] = func_call_match.string
                    code_index+=1
                elif num_match != None:
                    code[code_index]["opcode"] = opcode.PUSH
                    code[code_index]["arg"] = int(data[i])
                    code[code_index]["source"] = num_match.string
                    code_index+=1
                else:
                    assert data[i] in vars, "variable " + data[i] + " has not been defined!"
                    code[code_index]["opcode"] = opcode.PUSH
                    code[code_index]["arg"] = vars[data[i]]
                    code[code_index]["source"] = data[i]
                    code_index+=1

    for i in range(len(ifbuffer)):
        assert "then" in ifbuffer[i], "'if' structure isn't closed! (you probably lost a 'then')"
        ifloc = ifbuffer[i]["if"]
        thenloc = ifbuffer[i]["then"]
        if "else" in ifbuffer[i]:
            elseloc = ifbuffer[i]["else"]
            code[ifloc]["arg"] = elseloc+1
            code[elseloc]["arg"] = thenloc
            code[ifloc]["source"] = "if"
            code[elseloc]["source"] = "else"
        else:
            code[ifloc]["arg"] = thenloc
            code[ifloc]["source"] = "if"
        code[thenloc]["source"] = "then"

    for i in range(len(loopbuffer)):
        assert "end" in loopbuffer[i], "'loop' structure isn't closed! (you probably lost a 'loopend')"
        looploc = loopbuffer[i]["loop"]
        jumploc = loopbuffer[i]["jump"]
        endloc = loopbuffer[i]["end"]
        code[jumploc]["arg"] = (endloc+1)
        code[endloc]["arg"] = looploc
    if "arg" not in code[0]:
        code[0]["arg"] = 1
    code[0]["source"] = "<generated>"
    code[code_index]["opcode"] = opcode.HLT
    code[code_index]["source"] = "<generated>"
    return code

def translate(input, output):
    ifile = open(input, "r", encoding="utf-8")
    ofile = open(output, "w", encoding="utf-8")
    result = []
    code = parse_all(ifile.read())
    for i in range(len(code)):
        out_inst = code[i]
        if code[i] != 0 and code[i] != {}:
            out_inst = dict(index=i, value=out_inst)
            result.append(json.dumps(out_inst))
    ofile.write("[" + ",\n".join(result) + "]")
    ofile.close()
    return code

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: translator.py <input_file> <target_file>"
    myself, input, output = sys.argv
    translate(input, output)




