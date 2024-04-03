from components.errors import (
    RTError,
    InvalidSyntaxError,
    TooManyVariablesError,
    TooManyNestedError,
    StackOverFlowError
)
from runner import run


class TestNumbersArithmetic:

    def test_plus(self):
        result, error = run("6+3")
        assert result.value == 9, error

    def test_minus(self):
        result, error = run("6-3")
        assert result.value == 3, error

    def test_mul(self):
        result, error = run("6*3")
        assert result.value == 18, error

    def test_div(self):
        result, error = run("6/3")
        assert result.value == 2.0, error

    def test_div_by_zero(self):
        _, error = run("6/0")
        assert isinstance(error, RTError) and error.details == "Division by zero"


class TestNumbersOperations:
    def test_ee(self):
        result, error = run("6==6")
        assert result.value == 1, error

    def test_ne(self):
        result, error = run("6!=6")
        assert result.value == 0, error

    def test_gt(self):
        result, error = run("6>3")
        assert result.value == 1, error

    def test_gt_negative(self):
        result, error = run("6<3")
        assert result.value == 0, error

    def test_lt(self):
        result, error = run("3<6")
        assert result.value == 1, error

    def test_lt_negative(self):
        result, error = run("3>6")
        assert result.value == 0, error

    def test_gte(self):
        result, error = run("6>=3")
        assert result.value == 1, error

    def test_gte_equals(self):
        result, error = run("6>=6")
        assert result.value == 1, error

    def test_gte_negative(self):
        result, error = run("6<=3")
        assert result.value == 0, error

    def test_lte(self):
        result, error = run("3<=6")
        assert result.value == 1, error

    def test_lte_equals(self):
        result, error = run("3<=3")
        assert result.value == 1, error

    def test_lte_negative(self):
        result, error = run("3>=6")
        assert result.value == 0, error

    def test_multiple_and_operations(self):
        result, error = run("6>3 AND 6!=3")
        assert result.value == 1, error

    def test_multiple_and_false_operations(self):
        result, error = run("6>3 AND 6==3")
        assert result.value == 0, error

    def test_multiple_or_operations(self):
        result, error = run("6>3 OR 6==3")
        assert result.value == 1, error

    def test_multiple_or_false_operations(self):
        result, error = run("6<3 OR 6==3")
        assert result.value == 0, error


class TestVariable:
    def test_variable(self):
        result, error = run("VAR x=3")
        assert result.value == 3, error

    def test_variable_error(self):
        _, error = run("VAR 2")
        assert isinstance(error, InvalidSyntaxError) and error.details == "Expected identifier"


class TestIf:
    def test_if(self):
        result, error = run("IF 5>3 THEN 1")
        assert result.value == 1, error

    def test_if_not(self):
        result, error = run("IF NOT 5<3 THEN 1")
        assert result.value == 1, error

    def test_if_else(self):
        result, error = run("IF 5<3 THEN 1 ELSE 2")
        assert result.value == 2, error

    def test_if_elif(self):
        result, error = run("IF 5<3 THEN 1 ELIF 5>3 THEN 2")
        assert result.value == 2, error

    def test_if_elif_else(self):
        result, error = run("IF 5==3 THEN 1 ELIF 5<3 THEN 2 ELSE 3")
        assert result.value == 3, error


class TestWhile:
    def test_while(self):
        run("VAR x=3")
        _, error = run("WHILE x>0 THEN VAR x=x-1")
        assert error is None
        result, error = run("x")
        assert result.value == 0, error


class TestCustomError:
    def test_too_many_variables_assigned(self):
        run("VAR w=3")
        run("VAR x=3")
        run("VAR y=3")
        _, error = run("VAR z=3")
        assert isinstance(error, TooManyVariablesError) and error.details == "Too Many Variables Assigned"

    def test_too_many_while_nested(self):
        run("VAR x=3")
        _, error = run("WHILE x>5 THEN WHILE x>3 THEN WHILE x>4 VAR x=x-1")
        assert isinstance(error, TooManyNestedError) and error.details == "'WHILE'"

    def test_too_many_if_nested(self):
        run("VAR x=3")
        _, error = run("IF x>5 THEN IF x>3 THEN IF x>4 VAR x=x-1")
        assert isinstance(error, TooManyNestedError) and error.details == "'IF'"

    def test_maximum_result(self):
        _, error = run("2147483647 + 1")
        assert isinstance(error, StackOverFlowError) and error.details == "Result is too big"

    def test_minimum_result(self):
        _, error = run("-2147483648 - 1")
        assert isinstance(error, StackOverFlowError) and error.details == "Result is too small"
