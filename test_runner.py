from stack_machine import *
from translator import *
import sys

prelinked_tests = dict(
    cat = dict(
        code="golden_tests/tests/cat.leaf",
        test="golden_tests/tests/cat.json",
        output="golden_tests/output/cat_out.txt",
        logs="golden_tests/output/cat.log"
    ),
    hello = dict(
        code="golden_tests/tests/hello.leaf",
        test="golden_tests/tests/hello.json",
        output="golden_tests/output/hello_out.txt",
        logs="golden_tests/output/hello.log"
    ),
    hello_user_name = dict(
        code="golden_tests/tests/hello_user_name.leaf",
        test="golden_tests/tests/hello_user_name.json",
        output="golden_tests/output/hello_user_name_out.txt",
        logs="golden_tests/output/hello_user_name.log"
    ),
    prob1 = dict(
        code="golden_tests/tests/prob1.leaf",
        test="golden_tests/tests/prob1.json",
        output="golden_tests/output/prob1_out.txt",
        logs="golden_tests/output/prob1.log"
    ),
)

test_names = list(prelinked_tests.keys())
if len(sys.argv) == 5:
    myself, cdfile, tsfile, oufile, lofile = sys.argv
elif len(sys.argv) == 2:
    assert sys.argv[1] in prelinked_tests, "No test found with that name. Available tests: ".join(str(x)+'' for x in test_names)
    cdfile = prelinked_tests[sys.argv[1]]["code"]
    tsfile = prelinked_tests[sys.argv[1]]["test"]
    oufile = prelinked_tests[sys.argv[1]]["output"]
    lofile = prelinked_tests[sys.argv[1]]["logs"]
else:
    print("Usage: test_runner.py <test_name>")
    print("or")
    print("test_runner.py <code_file> <test_file> <output_file> <logs_file>")
    quit(1)

codefile = open(cdfile, "r", encoding="utf-8")
testfile = open(tsfile, "r", encoding="utf-8")
outfile = open(oufile, "w", encoding="utf-8")
logfile = open(lofile, "w", encoding="utf-8")

test = json.loads(testfile.read())
testfile.close()

assert "input" in test, "no program input!"
assert "expected" in test, "no output to compare to!"


code = parse_all(codefile.read())
codefile.close()
result = simulate(code, 200, test["input"])
outp = result[1]
logs = []
for i in range(len(result[0])):
    logs.append(json.dumps(result[0][i]))
logfile.write("[" + ",\n".join(logs) + "]")
outp = "".join(str(x)+'' for x in outp)
outfile.write(outp)

logfile.close()
outfile.close()

quitcode = None
if outp == test["expected"]:
    print("(" + testfile + ", " + cdfile + ") " + "output: '" + outp + "', expected: '" + test["expected"] + "'" + ", OK")
else:
    print("(" + testfile + ", " + cdfile + ") " + "output: '" + outp + "', expected: '" + test["expected"] + "'" + ", FAIL")
    quitcode = 1
quit(quitcode)