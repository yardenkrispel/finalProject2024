import string
from collections import defaultdict

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
from components.errors import (
    IllegalCharError,
    ExpectedCharError,
    TooManyNestedError
)

MAXIMUM_TIMES_NESTED = 3
KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELIF',
    'ELSE',
    'WHILE',
    'THEN'
]


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(-1, 0, -1, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def add_token_with_advance(self, token_type):
        token = Token(token_type, pos_start=self.pos)
        self.advance()
        return token

    def skip_whitespace(self):
        while self.current_char in ' \t':
            self.advance()

    def generate_tokens(self):
        collected_tokens = []

        mapping_sign_to_tokens = {'+': PLUS, '-': MINUS, '*': MUL, '/': DIV, '(': LPAREN, ')': RPAREN}

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.skip_whitespace()
            elif self.current_char.isdigit():
                collected_tokens.append(self.make_number())
            elif self.current_char.isalpha():
                collected_tokens.append(self.make_identifier())
            elif mapping_sign_to_tokens.get(self.current_char):
                collected_tokens.append(self.add_token_with_advance(mapping_sign_to_tokens[self.current_char]))
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                collected_tokens.append(token)
            elif self.current_char == '=':
                collected_tokens.append(self.make_equals())
            elif self.current_char == '<':
                collected_tokens.append(self.make_less_than())
            elif self.current_char == '>':
                collected_tokens.append(self.make_greater_than())
            else:
                start_position = self.pos.copy()
                character = self.current_char
                self.advance()
                return [], IllegalCharError(start_position, self.pos, f"'{character}'")

        collected_tokens.append(Token(EOF, pos_start=self.pos))
        error = self.make_sure_no_more_than_x_nested(collected_tokens)
        if error:
            return [], error
        return collected_tokens, None  # 3+5=>[3,+,5,EOF]

    def make_sure_no_more_than_x_nested(self, collected_tokens):
        counter_if_while = defaultdict(int)
        for token in collected_tokens:
            if token.value in {"WHILE", "IF"}:
                counter_if_while[token.value] += 1
            if counter_if_while[token.value] >= MAXIMUM_TIMES_NESTED:
                return TooManyNestedError(self.pos.copy(), self.pos, f"'{token.value}'")
        return None

    def make_number(self):
        number_string = ''
        decimal_point_count = 0
        start_position = self.pos.copy()

        while self.current_char is not None and self.current_char in f'{string.digits}.':
            if self.current_char == '.' and decimal_point_count == 1:
                break
            decimal_point_count += self.current_char == '.'
            number_string += self.current_char
            self.advance()

        if decimal_point_count == 0:
            return Token(INT, int(number_string), start_position, self.pos)
        return Token(FLOAT, float(number_string), start_position, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in f"{string.ascii_letters}_{string.digits}":
            id_str += self.current_char
            self.advance()

        tok_type = KEYWORD if id_str in KEYWORDS else IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


class Position:
    def __init__(self, idx, ln, col, txt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.txt = txt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.txt)
