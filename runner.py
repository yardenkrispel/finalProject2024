from components.interpeter import Interpreter
from components.tokenizer import Lexer
from components.parser import Parser
from components.number import Number


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def __len__(self):
        return len(self.symbols)

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value


global_symbol_table = SymbolTable()
global_symbol_table.set("FALSE", Number(0))
global_symbol_table.set("TRUE", Number(1))


def run(text):
    # Generate tokens
    lexer = Lexer(text)
    tokens, error = lexer.generate_tokens()
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
