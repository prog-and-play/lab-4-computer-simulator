"""LISP Parser - builds AST from tokens."""

from typing import List, Optional

from src.lexer import Lexer
from src.types import ASTNode, ASTNodeType, Token, TokenType


class Parser:
    """Parses LISP tokens into an AST."""

    def __init__(self, tokens: List[Token]) -> None:
        """Initialize parser with tokens."""
        self.tokens = tokens
        self.pos = 0

    def error(self, msg: str) -> None:
        """Raise a parser error."""
        token = self.current_token()
        raise SyntaxError(f"Parser error at {token.line}:{token.column}: {msg}")

    def current_token(self) -> Token:
        """Get current token without consuming."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token

    def peek_token(self, offset: int = 1) -> Token:
        """Peek at next token."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error."""
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type}, got {token.type}")
        return self.advance()

    def parse(self) -> ASTNode:
        """Parse a complete program."""
        if self.current_token().type == TokenType.EOF:
            self.error("Empty program")

        expr = self.parse_expr()

        if self.current_token().type != TokenType.EOF:
            self.error("Unexpected token after expression")

        return expr

    def parse_expr(self) -> ASTNode:
        """Parse an expression."""
        token = self.current_token()

        if token.type == TokenType.NUMBER:
            self.advance()
            return ASTNode(ASTNodeType.NUMBER, token.value)

        if token.type == TokenType.STRING:
            self.advance()
            return ASTNode(ASTNodeType.STRING, token.value)

        if token.type == TokenType.SYMBOL:
            self.advance()
            return ASTNode(ASTNodeType.SYMBOL, token.value)

        if token.type == TokenType.LPAREN:
            self.advance()
            return self.parse_form()

        self.error(f"Unexpected token: {token.type}")

    def parse_form(self) -> ASTNode:
        """Parse an S-expression form."""
        token = self.current_token()

        if token.type == TokenType.SYMBOL:
            symbol = token.value
            self.advance()

            if symbol == "defun":
                return self.parse_defun()
            elif symbol == "setq":
                return self.parse_setq()
            elif symbol == "if":
                return self.parse_if()
            elif symbol == "loop":
                return self.parse_loop()
            elif symbol == "print":
                return self.parse_print()
            else:
                return self.parse_function_call(symbol)
        else:
            self.error(f"Expected symbol, got {token.type}")

    def parse_defun(self) -> ASTNode:
        """Parse (defun name (args) body)."""
        name_token = self.expect(TokenType.SYMBOL)
        name = name_token.value

        self.expect(TokenType.LPAREN)
        args = self.parse_arg_list()
        self.expect(TokenType.RPAREN)

        body = self.parse_expr()

        self.expect(TokenType.RPAREN)

        node = ASTNode(ASTNodeType.DEFUN, name)
        node.children = [ASTNode(ASTNodeType.SYMBOL, arg) for arg in args]
        node.children.append(body)
        return node

    def parse_arg_list(self) -> List[str]:
        """Parse argument list."""
        args = []
        while self.current_token().type == TokenType.SYMBOL:
            args.append(self.advance().value)
        return args

    def parse_setq(self) -> ASTNode:
        """Parse (setq name value)."""
        name_token = self.expect(TokenType.SYMBOL)
        name = name_token.value
        value = self.parse_expr()

        self.expect(TokenType.RPAREN)

        node = ASTNode(ASTNodeType.SETQ, name)
        node.children = [value]
        return node

    def parse_if(self) -> ASTNode:
        """Parse (if cond then else)."""
        cond = self.parse_expr()
        then_expr = self.parse_expr()
        else_expr = self.parse_expr()

        self.expect(TokenType.RPAREN)

        node = ASTNode(ASTNodeType.IF)
        node.children = [cond, then_expr, else_expr]
        return node

    def parse_loop(self) -> ASTNode:
        """Parse (loop n expr)."""
        n = self.parse_expr()
        expr = self.parse_expr()

        self.expect(TokenType.RPAREN)

        node = ASTNode(ASTNodeType.LOOP)
        node.children = [n, expr]
        return node

    def parse_print(self) -> ASTNode:
        """Parse (print expr)."""
        expr = self.parse_expr()

        self.expect(TokenType.RPAREN)

        node = ASTNode(ASTNodeType.PRINT)
        node.children = [expr]
        return node

    def parse_function_call(self, func_name: str) -> ASTNode:
        """Parse (func arg1 arg2 ...)."""
        args = []

        while self.current_token().type != TokenType.RPAREN:
            args.append(self.parse_expr())

        self.expect(TokenType.RPAREN)

        node = ASTNode(ASTNodeType.FUNCTION_CALL, func_name)
        node.children = args
        return node


def parse_lisp(source: str) -> ASTNode:
    """Parse LISP source code into AST."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
