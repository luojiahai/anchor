import os
import sys
import anchor.ply.yacc as yacc
import anchor.lex as lex
import anchor.token as token


__all__ = ['Parser', 'AnchorParser',]


class Parser:

    tokens = ()
    precedence = ()

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', 0)
        self.names = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"

        # Build the lexer and parser
        self.lexer = lex.AnchorLexer()
        self.lexer.build(debug=self.debug)
        self.parser = yacc.yacc(
            module=self,
            debug=self.debug,
            debugfile=self.debugfile
        )

    def parse(self, data):
        self.lexer.test(data)
        return self.parser.parse(data)


class AnchorParser(Parser):

    # Tokens list
    tokens = lex.AnchorLexer.tokens

    # Precedence rules
    precedence = (
        ('left', token.OR,),
        ('left', token.AND,),
        ('right', token.NOT,),
        ('nonassoc', token.EQEQUAL, token.NOTEQUAL, token.LESS, token.GREATER, token.LESSEQUAL, token.GREATEREQUAL,),
        ('left', token.PLUS, token.MINUS,),
        ('left', token.STAR, token.SLASH, token.DOUBLESLASH, token.PERCENT,),
        ('right', token.UPLUS, token.UMINUS,),
        ('left', token.DOUBLESTAR,),
    )

    def p_program(self, p):
        '''program : block
                   | empty'''
        p[0] = p[1]

    def p_block(self, p):
        '''block : statements'''
        p[0] = p[1]

    def p_statements(self, p):
        '''statements : statements statement
                      | statement'''
        if (len(p) == 3):
            statements = p[1]
            if (p[2]): statements.append(p[2])
            p[0] = statements
        elif (len(p) == 2):
            p[0] = [p[1]]

    def p_statement_assignment(self, p):
        '''statement : NAME EQUAL expression SEMI'''
        # TODO
        pass

    def p_statement_if(self, p):
        '''statement : IF expression THEN block elif END'''
        # TODO
        expression = p[2]
        block = p[4]
        statement_elif = p[5]
        p[0] = (expression, block, statement_elif)

    def p_statement_ifelse(self, p):
        '''statement : IF expression THEN block block_else END
                     | IF expression THEN block END'''
        # TODO
        if (len(p) == 7):
            expression = p[2]
            block = p[4]
            block_else = p[5]
            p[0] = (expression, block, block_else)
        elif (len(p) == 6):
            expression = p[2]
            block = p[4]
            p[0] = (expression, block)

    def p_elif(self, p):
        '''elif : ELIF expression THEN block elif'''
        # TODO
        expression = p[2]
        block = p[4]
        statement_elif = p[5]
        p[0] = [(expression, block)] + statement_elif

    def p_elif_else(self, p):
        '''elif : ELIF expression THEN block block_else
                | ELIF expression THEN block'''
        # TODO
        if (len(p) == 6):
            expression = p[2]
            block = p[4]
            block_else = p[5]
            p[0] = [(expression, block, block_else)]
        elif (len(p) == 5):
            expression = p[2]
            block = p[4]
            p[0] = [(expression, block)]

    def p_block_else(self, p):
        '''block_else : ELSE block'''
        # TODO
        p[0] = p[2]

    def p_statement_iterate(self, p):
        '''statement : ITERATE expression FOR NAME BEGIN block END'''
        # TODO
        pass

    def p_statement_while(self, p):
        '''statement : WHILE expression BEGIN block END'''
        # TODO
        pass

    def p_statement_break(self, p):
        '''statement : BREAK SEMI'''
        p[0] = p[1]

    def p_statement_continue(self, p):
        '''statement : CONTINUE SEMI'''
        p[0] = p[1]

    def p_statement_classdef(self, p):
        '''statement : CLASS LSQB annotations RSQB NAME INHERIT LPAR NAME RPAR BEGIN block END
                     | CLASS LSQB annotations RSQB NAME BEGIN block END'''
        # TODO
        pass

    def p_statement_methoddef(self, p):
        '''statement : METHOD LSQB annotations RSQB NAME LPAR parameters RPAR RARROW NAME BEGIN block END
                     | METHOD LSQB annotations RSQB NAME LPAR RPAR RARROW NAME BEGIN block END'''
        # TODO
        pass

    def p_statement_functiondef(self, p):
        '''statement : FUNCTION NAME LPAR parameters RPAR RARROW NAME BEGIN block END
                     | FUNCTION NAME LPAR RPAR RARROW NAME BEGIN block END'''
        # TODO
        pass

    def p_statement_property(self, p):
        '''statement : PROPERTY LSQB annotations RSQB NAME SEMI'''
        # TODO
        pass

    def p_annotations(self, p):
        '''annotations : _annotations COMMA
                       | _annotations'''
        p[0] = p[1] 

    def p__annotations(self, p):
        '''_annotations : _annotations COMMA annotation
                        | annotation'''
        if (len(p) == 4):
            annotations = p[1]
            if (p[3]): annotations.append(p[3])
            p[0] = annotations
        elif (len(p) == 2):
            annotation = p[1]
            p[0] = [annotation]

    def p_annotation(self, p):
        '''annotation : PUBLIC
                      | PRIVATE
                      | PROTECTED
                      | GET
                      | SET
                      | REF
                      | VAL'''
        p[0] = p[1]

    def p_parameters(self, p):
        '''parameters : _parameters COMMA
                      | _parameters'''
        p[0] = p[1] 

    def p__parameters(self, p):
        '''_parameters : _parameters COMMA parameter
                       | parameter'''
        if (len(p) == 4):
            parameters = p[1]
            if (p[3]): parameters.append(p[3])
            p[0] = parameters
        if (len(p) == 2):
            parameter = p[1]
            p[0] = [parameter]

    def p_parameter(self, p):
        '''parameter : NAME COLON NAME LSQB annotations RSQB
                     | NAME COLON NAME
                     | NAME'''
        # TODO
        pass

    def p_statement_return(self, p):
        '''statement : RETURN expression SEMI'''
        p[0] = p[2]

    def p_statement_expression(self, p):
        '''statement : expression SEMI'''
        p[0] = p[1]

    def p_expression_or(self, p):
        '''expression : expression OR expression'''
        p[0] = p[1] or p[3]

    def p_expression_and(self, p):
        '''expression : expression AND expression'''
        p[0] = p[1] and p[3]

    def p_exrepssion_not(self, p):
        '''expression : NOT expression'''
        p[0] = not p[2]

    def p_expression_relational(self, p):
        '''expression : expression EQEQUAL expression
                      | expression NOTEQUAL expression
                      | expression LESS expression
                      | expression LESSEQUAL expression
                      | expression GREATER expression
                      | expression GREATEREQUAL expression'''
        left = p[1]
        right = p[3]
        operator = token.EXACT_TOKEN_TYPES[p[2]]
        if (operator == token.EQEQUAL):
            p[0] = left == right
        elif (operator == token.NOTEQUAL):
            p[0] = left != right
        elif (operator == token.LESS):
            p[0] = left < right
        elif (operator == token.LESSEQUAL):
            p[0] = left <= right
        elif (operator == token.GREATER):
            p[0] = left > right
        elif (operator == token.GREATEREQUAL):
            p[0] = left >= right
    
    def p_expression_binary(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression STAR expression
                      | expression DOUBLESTAR expression
                      | expression SLASH expression
                      | expression DOUBLESLASH expression
                      | expression PERCENT expression'''
        left = p[1]
        right = p[3]
        operator = token.EXACT_TOKEN_TYPES[p[2]]
        if (operator == token.PLUS):
            p[0] = left + right
        elif (operator == token.MINUS):
            p[0] = left - right
        elif (operator == token.STAR):
            p[0] = left * right
        elif (operator == token.DOUBLESTAR):
            p[0] = left ** right
        elif (operator == token.SLASH):
            p[0] = left / right
        elif (operator == token.DOUBLESLASH):
            p[0] = left // right
        elif (operator == token.PERCENT):
            p[0] = left % right

    def p_expression_unary(self, p):
        '''expression : PLUS expression %prec UPLUS
                      | MINUS expression %prec UMINUS'''
        right = p[2]
        operator = token.EXACT_TOKEN_TYPES[p[1]]
        if (operator == token.PLUS):
            p[0] = +right
        elif (operator == token.MINUS):
            p[0] = -right

    def p_expression_group(self, p):
        '''expression : LPAR expression RPAR'''
        p[0] = p[2]

    def p_expression_dotname(self, p):
        '''expression : expression DOT NAME'''
        # TODO
        pass

    def p_expression_call(self, p):
        '''expression : expression LPAR arguments RPAR
                      | expression LPAR RPAR'''
        # TODO
        pass

    def p_arguments(self, p):
        '''arguments : args COMMA
                     | args'''
        p[0] = p[1] 

    def p_args(self, p):
        '''args : args COMMA expression
                | expression'''
        if (len(p) == 4):
            args = p[1]
            if (p[3]): args.append(p[3])
            p[0] = args
        elif (len(p) == 2):
            expression = p[1]
            p[0] = [expression]

    def p_expression_true(self, p):
        '''expression : TRUE'''
        p[0] = True

    def p_expression_false(self, p):
        '''expression : FALSE'''
        p[0] = False

    def p_expression_null(self, p):
        '''expression : NULL'''
        p[0] = None

    def p_expression_name(self, p):
        '''expression : NAME'''
        p[0] = p[1]

    def p_expression_integer(self, p):
        '''expression : INTEGER'''
        p[0] = int(p[1])

    def p_expression_float(self, p):
        '''expression : FLOAT'''
        p[0] = float(p[1])

    def p_expression_complex(self, p):
        '''expression : COMPLEX'''
        p[0] = complex(p[1])

    def p_expression_string(self, p):
        '''expression : STRING'''
        p[0] = str(p[1])

    def p_expression_list(self, p):
        '''expression : LSQB RSQB'''
        # TODO
        pass

    def p_expression_dict(self, p):
        '''expression : LBRACE RBRACE'''
        # TODO
        pass

    def p_empty(self, p):
        '''empty : '''
        pass

    def p_error(self, p):
        print(f'ERROR: {p}', file=sys.stderr)
        pass
