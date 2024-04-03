from components.errors import RTError, TooManyVariablesError, StackOverFlowError
from components.number import Number
from components.token_types import (
    GT,
    LTE,
    GTE,
    EE,
    NE,
    MUL,
    PLUS,
    MINUS,
    DIV,
    KEYWORD,
    LT
)
from components.tokenizer import Position

MAXIMUM_NUMBER_OF_VARIABLES = 3


class Interpreter:
    MAX_NUMBER = 2 ** 31 - 1
    MIN_NUMBER = -2 ** 31

    def __init__(self):
        self.visit_methods = {
            'NumberNode': self.visit_number_node,
            'VarAccessNode': self.visit_var_access_node,
            'VarAssignNode': self.visit_var_assign_node,
            'BinOpNode': self.visit_bin_op_node,
            'UnaryOpNode': self.visit_unary_op_node,
            'IfNode': self.visit_if_node,
            'WhileNode': self.visit_while_node,
        }

    def visit(self, node, context):
        node_type_name = type(node).__name__
        method = self.visit_methods.get(node_type_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise ValueError(f'No visit_{type(node).__name__} method defined')

    @staticmethod
    def visit_number_node(node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    @staticmethod
    def visit_var_access_node(node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_var_assign_node(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res

        if MAXIMUM_NUMBER_OF_VARIABLES + 2 <= len(context.symbol_table):
            # +2 because TRUE AND FALSE
            return res.failure(TooManyVariablesError(
                Position(0, 0, 0, ''), Position(1, 0, 1, ''),
                "Too Many Variables Assigned",
                context=context
            ))
        context.symbol_table.set(var_name, value)
        return res.success(value)

    @classmethod
    def __limit_result(cls, result: Number):
        error = None
        if result.value > cls.MAX_NUMBER:
            error = StackOverFlowError(result.pos_start, result.pos_end, "Result is too big")
        elif result.value < cls.MIN_NUMBER:
            error = StackOverFlowError(result.pos_start, result.pos_end, "Result is too small")
        return result, error

    def visit_bin_op_node(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        operations = {
            PLUS: left.added_to,
            MINUS: left.subbed_by,
            MUL: left.multed_by,
            DIV: left.dived_by,
            EE: left.get_comparison_eq,
            NE: left.get_comparison_ne,
            LT: left.get_comparison_lt,
            GT: left.get_comparison_gt,
            LTE: left.get_comparison_lte,
            GTE: left.get_comparison_gte,
        }

        if node.op_tok.type in operations:
            result, error = operations[node.op_tok.type](right)
            if not error:
                result, error = self.__limit_result(result)
        elif node.op_tok.matches(KEYWORD, 'AND'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(KEYWORD, 'OR'):
            result, error = left.ored_by(right)
        else:
            error = None
            result = None

        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))  # 3+5=>8

    def visit_unary_op_node(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(KEYWORD, 'NOT'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_if_node(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_while_node(self, node, context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)


class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self
