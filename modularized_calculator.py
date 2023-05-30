#! /usr/bin/python3
from decimal import Decimal, ROUND_HALF_UP


def read_number(line, index):
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1
    token = {'type': 'NUMBER', 'number': number}
    return token, index


def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1


def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1


def read_multiply(line, index):
    token = {'type': 'MULTIPLY'}
    return token, index + 1


def read_divide(line, index):
    token = {'type': 'DEVIDE'}
    return token, index + 1


def read_parentheses(line, index):
    if line[index] == "(":
        token = {'type': 'LEFT_PARENTHESIS'}
    elif line[index] == ")":
        token = {'type': 'RIGHT_PARENTHESIS'}
    return token, index + 1


def read_function_name(line, index):
    function_name = ''
    while line[index].isalpha():
        function_name += line[index]
        index += 1
    if function_name == 'abs':
        token = {'type': 'ABS'}
    elif function_name == 'int':
        token = {'type': 'INT'}
    elif function_name == 'round':
        token = {'type': 'ROUND'}
    else:
        print('Invalid syntax')
        exit(1)
    return token, index


def tokenize(line):
    tokens = []
    index = 0
    is_append_token = True
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == '+':
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index)
        elif line[index] == '*':
            (token, index) = read_multiply(
                line, index)
        elif line[index] == '/':
            (token, index) = read_divide(line, index)
        elif line[index] == '(' or line[index] == ')':
            (token, index) = read_parentheses(
                line, index)
        elif line[index] == 'a' or line[index] == 'i' or line[index] == 'r':
            (token, index) = read_function_name(
                line, index)
        elif line[index] == ' ':
            index += 1
            is_append_token = False
        else:
            print('Invalid character found: ' + line[index])
            exit(1)

        if is_append_token:
            tokens.append(token)
        else:
            is_append_token = True
    return tokens


# <式> = <項> ｜ <式> + <項> | <式> - <項>
def expression(tokens, index):
    (expression_value, index) = term(tokens, index)
    while index < len(tokens) and (tokens[index]['type'] == "PLUS" or tokens[index]['type'] == 'MINUS'):
        if tokens[index]['type'] == 'PLUS':
            index += 1
            (term_value, index) = term(tokens, index)
            expression_value = expression_value + term_value
        elif tokens[index]['type'] == 'MINUS':
            index += 1
            (term_value, index) = term(tokens, index)
            expression_value = expression_value - term_value

    return expression_value, index


# <項> = <因子> | <項> * <因子> | <項> / <因子>
def term(tokens, index):
    (term_value, index) = factor(tokens, index)
    while index < len(tokens) and (tokens[index]['type'] == 'MULTIPLY' or tokens[index]['type'] == 'DEVIDE'):
        if tokens[index]['type'] == 'MULTIPLY':
            index += 1
            (factor_value, index) = factor(tokens, index)
            term_value = term_value * factor_value
        elif tokens[index]['type'] == 'DEVIDE':
            index += 1
            (factor_value, index) = factor(tokens, index)
            term_value = term_value / factor_value

    return term_value, index


# <因子> = <数値> | (<式>) | abs(<式>) | int(<式>) | round(<式>)
def factor(tokens, index):
    if index < len(tokens):
        if tokens[index]['type'] == 'NUMBER' or tokens[index]['type'] == 'MINUS':
            factor_value, index = numerical_value(tokens, index)
        elif tokens[index]['type'] == 'LEFT_PARENTHESIS':
            index += 1
            factor_value, index = expression(tokens, index)
            assert tokens[index]['type'] == 'RIGHT_PARENTHESIS', 'No )'
            index += 1
        elif tokens[index]['type'] == 'ABS' or tokens[index]['type'] == 'INT' or tokens[index]['type'] == 'ROUND':
            function_name = tokens[index]['type']
            index += 1
            factor_value, index = function_return_value(
                tokens, index, function_name)
        else:
            print('Invalid syntax (factor)')
            exit(1)
    return factor_value, index


# <数値> = 'NUMBER' | -'NUMBER'
# NUMBER: 負でない数
def numerical_value(tokens, index):
    if tokens[index]['type'] == 'MINUS':
        index += 1
        assert tokens[index]['type'] == 'NUMBER', 'Invalid syntax (numerical_value)'
        non_negative_integer = tokens[index]['number']
        return non_negative_integer * (-1), index + 1
    elif tokens[index]['type'] == 'NUMBER':
        non_negative_integer = tokens[index]['number']
        return non_negative_integer, index + 1


# abs(<式>) | int(<式>) | round(<式>)
def function_return_value(tokens, index, function_name):
    assert tokens[index]['type'] == 'LEFT_PARENTHESIS', 'Not ('
    index += 1
    value, index = expression(tokens, index)
    if function_name == 'ABS':
        function_value = abs(value)
    elif function_name == 'INT':
        function_value = int(value)
    elif function_name == 'ROUND':
        function_value = int(Decimal(str(value)).quantize(
            Decimal('0'), rounding=ROUND_HALF_UP))
    assert tokens[index]['type'] == 'RIGHT_PARENTHESIS', 'Not )'
    index += 1
    return function_value, index


def evaluate(tokens):
    answer = 0
    tokens.insert(0, {'type': 'PLUS'})  # Insert a dummy '+' token
    index = 1
    answer, index = expression(tokens, index)
    return answer


def test(line):
    tokens = tokenize(line)
    actual_answer = evaluate(tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print("FAIL! (%s should be %f but was %f)" %
              (line, expected_answer, actual_answer))


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("-9.5+8.0")    # 負の数
    test("5")  # 演算子がない式
    test("abs(-8.7)")  # 演算子がない式
    test("7+3")    # 加算のみ
    test("8.7-5.55")   # 減算のみ
    test("9.3*7.5")  # 乗算のみ
    test("14089/679")    # 除算のみ
    test("8*3+5/2-9*4/3")    # 計算の優先度 (括弧なしバージョン)
    test("(8+5*4)*6/2")  # 計算の優先度 (括弧ありバージョン)
    test("(8*(3+4/2))+9*(3*(2+4))")    # 計算の優先度 (二重括弧ありバージョン)
    test("abs(-9.5)")    # abs()
    test("int(7.5*3)")    # int()
    test("round(abs(-5.5*(7+2)))")    # round()
    test("round(int(4.6)*3.3)")  # round()
    test("int(abs(-9.5))*4*(int(-7.87)+8)")    # 非演算子に関数と数値、()のついた式が混ざっている場合
    test("1   +  4  * 5")    # 空白文字を読み飛ばせているか
    print("==== Test finished! ====\n")


run_test()

# use when trying your own input
# while True:
#     print('> ', end="")
#     line = input()
#     tokens = tokenize(line)
#     answer = evaluate(tokens)
#     print("answer = %f\n" % answer)
