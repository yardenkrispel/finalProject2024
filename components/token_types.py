INT = 'INT'                  # 7
FLOAT = 'FLOAT'              # 1.3
IDENTIFIER = 'IDENTIFIER'    # some variable [משתנה]
KEYWORD = 'KEYWORD'          # type of all the keywords like IF, WHILE, VAR, ...
PLUS = 'PLUS'                # +
MINUS = 'MINUS'              # -
MUL = 'MUL'                  # *
DIV = 'DIV'                  # /
EQ = 'EQ'                    # equals
LPAREN = 'LPAREN'            # ( parenthesis[סוגריים יעני]
RPAREN = 'RPAREN'            # )
EE = 'EE'                    # ==
NE = 'NE'                    # !=
LT = 'LT'                    # less than X<Y
GT = 'GT'                    # greater than X>Y
LTE = 'LTE'                  # less than equals X<=Y
GTE = 'GTE'                  # greater than equals X>=Y
EOF = 'EOF'                  # END OF FILE


# GIVEN :     3+4*5
# TOKENIZER : INT[1] PLUS INT[2] MUL INT[3]
# PARSER :    INT[2] MUL INT[3] PLUS INT[1]
# INTERPETER: 4*5=20+3=23
