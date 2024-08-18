# Лабораторная работа №3
Глебов Андрей Станиславович P3233
`forth | stack | neum | hw | instr | struct | stream | port | cstr | prob1`
(Вариант с упрощением)
---
## Язык программирования
### Синтаксис
Форма Бэкуса-Наура:
```
<name> ::= [A-Za-z_]+
<variable> ::= <name>
<def_variable> ::= <name>"="<number>
<set_variable> ::= <number> "="<name>
<variables> ::= <def_variable> | <set_variable> | <variable>
<number> ::= [0-9]+
<def_procedure> ::= <name>":"
<call_procedure> ::= "/"<name>
<procedures> ::= <def_procedure> | <call_procedure>
<string_print> ::= ".'"<text>"'"
<term> ::= <numbers> | <variables> | <prrocedures> | <string_prints>
<operator> ::= "+" | "-" | "*" | "/" | "%" | "." | "!" | in | drop | halt
<compare> ::= ">" | "<" | "=="
<if_then> ::= <compare> "if" <term> "then"
<if_else> ::= <compare> "if" <term> "else" <term> "then"
<loop> ::= <name> <number> "+" | "-" "loop" <term> "loopend"
```
### Операторы
``+`` - сумма двух чисел с вершины стека, ``[... a b] -> [... a+b]``
``-`` - разность двух чисел с вершины стека, ``[... a b] -> [... a-b]``
``*`` - умножение двух чисел с вершины стека, ``[... a b] -> [... a*b]``
``/`` - деление двух чисел с вершины стека, ``[... a b] -> [... a/b]``
``%`` - остаток от деления двух чисел с вершины стека, ``[... a b] -> [... a%b]``
``.`` - вывод числа с вершины стека, ``[... a] -> [output a]``
``!`` - разыменование числа с вершины стека, ``[... a] -> [... mem(a)]``
``in`` - считывание ввода и помещение на вершину стека, ``[...] -> [... input]``
``drop`` - удаление числа с вершины стека, ``[... a] -> [...]``
``halt`` - команда останова
## Организация памяти
Архитектура Фон-Неймана, то есть память данных и команд общая.
В ячейке 0 находится команда перехода на начало программы, c 1 до 249 находится код функций и программы, 250-499 - значения переменных, а дальше строки.
```
            Memory
+------------------------------+
| 0  : jmp N                   |
|    ...                       |
|    <function code>           |
|    ...                       |
| n   : program start          |
| n+1 : program                |
|    ...                       |
| 250 : variables              |
| 251 : variables              |
|    ...                       |
| 500 : strings                |
| 501 : strings                |
|    ...                       |
+------------------------------+
```
Строки хранятся по одному символу в ячейке и заканчиваются нулём.
Получение данных из памяти происходит по адресу на вершине стека.
## Система команд
Машинное слово -- передаётся как словарь. Получение инструкции из памяти получается через регистр IP, который можно либо защёлкнуть на один вверх, либо на конкретный адрес во время перехода. Защёлкивание IP на один вверх происходит всегда, когда не происходит переход.
## Транслятор
Транcлятор: [translator.py](translator.py)
Использование в командной строке: ``translator.py <input_file> <target_file>``
input_file - файл с кодом
target_file - файл для вывода машинного кода
Использование с import: вызвать функцию parse_all() с текстом кода.
## Модель процессора
### DataPath

### ControlUnit

## Тестирование
Тестирование выполняется скриптом [test_runner.py] (test_runner.py)
Тестирование в командной строке:
``test_runner.py <code_file> <test_file> <output_file> <logs_file>``
Golden-тесты (``test_runner.py <test_name>``)
- cat ([code](golden_tests/tests/cat.leaf)|[input](golden_tests/tests/cat.json)) - копирует символы из ввода в вывод
- hello ([code](golden_tests/tests/hello.leaf)|[input](golden_tests/tests/hello.json)) - выводит 'hello world!'
- hello_user_name ([code](golden_tests/tests/hello_user_name.leaf)|[input](golden_tests/tests/hello_user_name.json)) - получает из ввода имя пользователя и приветствует его
- prob1 ([code](golden_tests/tests/prob1.leaf)|[input](golden_tests/tests/prob1.json)) - находит сумму всех чисел, кратных 3 и 5 и строго меньше 1000
