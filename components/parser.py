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
    LPAREN,
    RPAREN,
    EOF,
    KEYWORD,
    IDENTIFIER,
    EQ,
    INT,
    FLOAT,
    LT
)
from components.errors import InvalidSyntaxError


class Parser:
    def __init__(self, tokens):
        self.current_tok = None
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
            ))
        return res

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        def parse_branch(keyword):
            """Parses a single if/elif branch and returns a tuple of (condition, expression) or None on failure."""
            if not self.current_tok.matches(KEYWORD, keyword):
                error_msg = f"Expected '{keyword}'"
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, error_msg
                )), None

            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res, None

            if not self.current_tok.matches(KEYWORD, 'THEN'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'THEN'"
                )), None

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res, None

            return res, (condition, expr)

        # Parse the initial if condition
        initial_res, initial_case = parse_branch('IF')
        if initial_res.error:
            return initial_res
        cases.append(initial_case)

        # Parse any elif conditions
        while self.current_tok.matches(KEYWORD, 'ELIF'):
            elif_res, elif_case = parse_branch('ELIF')
            if elif_res.error:
                return elif_res
            cases.append(elif_case)

        # Parse else case
        if self.current_tok.matches(KEYWORD, 'ELSE'):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

    def while_expr(self):
        res = ParseResult()

        def advance_and_register():
            res.register_advancement()
            self.advance()

        if not self.current_tok.matches(KEYWORD, 'WHILE'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'WHILE'"
            ))

        advance_and_register()
        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'THEN'"
            ))

        advance_and_register()
        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (INT, FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        if tok.type == IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        if tok.type == LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')'"
            ))

        if tok.matches(KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        if tok.matches(KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', '('"
        ))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (PLUS, MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.bin_op(self.atom, (), self.factor)

    def term(self):
        return self.bin_op(self.factor, (MUL, DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (PLUS, MINUS))

    def compare_expr(self):
        res = ParseResult()

        if self.current_tok.matches(KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.compare_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (EE, NE, LT, GT, LTE, GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(' or 'NOT'"
            ))

        return res.success(node)

    def expr(self):
        res = ParseResult()

        def advance_with_registration():
            res.register_advancement()
            self.advance()

        if self.current_tok.matches(KEYWORD, 'VAR'):
            advance_with_registration()

            if self.current_tok.type != IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))

            var_name = self.current_tok
            advance_with_registration()

            if self.current_tok.type != EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))

            advance_with_registration()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        # Attempt to parse a binary operation if not parsing a variable assignment
        node = res.register(self.bin_op(self.compare_expr, ((KEYWORD, 'AND'), (KEYWORD, 'OR'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-', '(' or 'NOT'"
            ))

        return res.success(node)

    def bin_op(self, func_a, ops=(), func_b=None):
        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end


class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self
