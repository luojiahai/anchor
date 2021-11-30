import anchor.ply.yacc as yacc
import anchor.lex as lex
import anchor.token as token
import anchor.ast as ast
import anchor.system as system


__all__ = ['AnchorParser',]


class Parser(object):

    tokens: tuple = ()
    precedence: tuple = ()

    def __init__(self, **kwargs):
        self.debuglex: bool = kwargs.get('debuglex', False)
        self.debugyacc: bool = kwargs.get('debugyacc', False)
        self.debuglog: bool = kwargs.get('debuglog', None)

        # Build the lexer and parser
        self.lexer: lex.AnchorLexer = lex.AnchorLexer()
        self.lexer.build(
            debug=self.debuglex, 
            debuglog=self.debuglog if self.debuglex else None,
        )
        self.parser = yacc.yacc(
            module=self,
            debug=self.debugyacc,
            debuglog=self.debuglog if self.debugyacc else None,
        )

    def parse(self, data: str) -> ast.ASTNode:
        if (self.debuglex): self.lexer.debug(data)
        return self.parser.parse(data)


class AnchorParser(Parser):

    # Tokens list
    tokens: tuple = lex.AnchorLexer.tokens

    # Precedence rules
    precedence: tuple = (
        ('left', token.OR,),
        ('left', token.AND,),
        ('right', token.NOT,),
        ('nonassoc', token.EQEQUAL, token.NOTEQUAL, 
            token.LESS, token.GREATER, token.LESSEQUAL, token.GREATEREQUAL,),
        ('left', token.PLUS, token.MINUS,),
        ('left', token.STAR, token.SLASH, token.DOUBLESLASH, token.PERCENT,),
        ('right', token.UPLUS, token.UMINUS,),
        ('left', token.DOUBLESTAR,),
    )

    def p_program(self, p):
        '''program : block
                   | empty'''
        p[0] = ast.Program(p[1])

    def p_block(self, p):
        '''block : statements'''
        p[0] = ast.Block(p[1])

    def p_statements(self, p):
        '''statements : statements statement
                      | statement'''
        if (len(p) == 3):
            statements = p[1]
            statement = p[2]
            if (statement): statements.append(statement)
            p[0] = statements
        elif (len(p) == 2):
            statement = p[1]
            p[0] = list([statement])

    def p_statement_assignment(self, p):
        '''statement : name EQUAL expression SEMI'''
        name = p[1]
        expression = p[3]
        p[0] = ast.Assignment(name, expression)

    def p_statement_if(self, p):
        '''statement : IF expression THEN block elifs END'''
        expression = p[2]
        block = p[4]
        elifs = p[5]
        p[0] = ast.If(expression, block, elifs=elifs)

    def p_statement_if_else(self, p):
        '''statement : IF expression THEN block elseblock END
                     | IF expression THEN block END'''
        if (len(p) == 7):
            expression = p[2]
            block = p[4]
            elseblock = p[5]
            p[0] = ast.If(expression, block, elseblock=elseblock)
        elif (len(p) == 6):
            expression = p[2]
            block = p[4]
            p[0] = ast.If(expression, block)

    def p_elifs(self, p):
        '''elifs : ELIF expression THEN block elifs'''
        expression = p[2]
        block = p[4]
        elifs = p[5]
        p[0] = list([ast.Elif(expression, block)]) + elifs

    def p_elifs_else(self, p):
        '''elifs : ELIF expression THEN block elseblock
                 | ELIF expression THEN block'''
        if (len(p) == 6):
            expression = p[2]
            block = p[4]
            elseblock = p[5]
            p[0] = list([ast.Elif(expression, block, elseblock)])
        elif (len(p) == 5):
            expression = p[2]
            block = p[4]
            p[0] = list([ast.Elif(expression, block)])

    def p_elseblock(self, p):
        '''elseblock : ELSE block'''
        p[0] = p[2]

    def p_statement_iterate(self, p):
        '''statement : ITERATE expression FOR name BEGIN block END'''
        iterable = p[2]
        variable = p[4]
        block = p[6]
        p[0] = ast.Iterate(iterable, variable, block)

    def p_statement_loop(self, p):
        '''statement : LOOP expression BEGIN block END'''
        expression = p[2]
        block = p[4]
        p[0] = ast.Loop(expression, block)

    def p_statement_functiondef(self, p):
        '''statement : FUNCTION name LPAR parameters RPAR \
                       RARROW expression BEGIN block END
                     | FUNCTION name LPAR RPAR \
                       RARROW expression BEGIN block END'''
        if (len(p) == 11):
            name = p[2]
            parameters = p[4]
            returntype = p[7]
            body = p[9]
            flags = dict({'returntype': returntype})
            p[0] = ast.FunctionDef(name, parameters, body, **flags)
        elif (len(p) == 10):
            name = p[2]
            parameters = list()
            returntype = p[7]
            body = p[8]
            flags = dict({'returntype': returntype})
            p[0] = ast.FunctionDef(name, parameters, body, **flags)

    def p_statement_classdef(self, p):
        '''statement : CLASS LSQB annotations RSQB name \
                       INHERIT LPAR name RPAR BEGIN block END
                     | CLASS LSQB annotations RSQB name \
                       BEGIN block END'''
        # TODO: annotations
        if (len(p) == 13):
            annotations = p[3]
            name = p[5]
            superclasses = [p[8]]
            block = p[11]
            p[0] = ast.ClassDef(name, superclasses, block)
        if (len(p) == 9):
            annotations = p[3]
            name = p[5]
            superclasses = []
            block = p[7]
            p[0] = ast.ClassDef(name, superclasses, block)

    def p_statement_property(self, p):
        '''statement : PROPERTY LSQB annotations RSQB name SEMI'''
        # TODO: annotations
        annotations = p[3]
        name = p[5]
        p[0] = ast.Property(name)

    def p_statement_methoddef(self, p):
        '''statement : METHOD LSQB annotations RSQB name LPAR parameters RPAR \
                       RARROW expression BEGIN block END
                     | METHOD LSQB annotations RSQB name LPAR RPAR \
                       RARROW expression BEGIN block END'''
        # TODO: annotations
        if (len(p) == 14):
            annotations = [p[3]]
            name = p[5]
            parameters = p[7]
            returntype = p[10]
            body = p[12]
            flags = dict({'returntype': returntype, 'ismethod': True})
            p[0] = ast.FunctionDef(name, parameters, body, **flags)
        elif (len(p) == 13):
            annotations = [p[3]]
            name = p[5]
            parameters = []
            returntype = p[9]
            body = p[11]
            flags = dict({'returntype': returntype, 'ismethod': True})
            p[0] = ast.FunctionDef(name, parameters, body, **flags)

    def p_annotations(self, p):
        '''annotations : _annotations COMMA
                       | _annotations'''
        p[0] = p[1] 

    def p__annotations(self, p):
        '''_annotations : _annotations COMMA annotation
                        | annotation'''
        if (len(p) == 4):
            annotations = p[1]
            annotation = p[3]
            if (annotation): annotations.append(annotation)
            p[0] = annotations
        elif (len(p) == 2):
            annotation = p[1]
            p[0] = list([annotation])

    def p_annotation(self, p):
        '''annotation : PUBLIC
                      | PRIVATE
                      | PROTECTED
                      | GET
                      | SET
                      | REF
                      | VAL'''
        # TODO
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
            parameter = p[3]
            if (parameter): parameters.append(parameter)
            p[0] = parameters
        if (len(p) == 2):
            parameter = p[1]
            p[0] = list([parameter])

    def p_parameter(self, p):
        '''parameter : name COLON name LSQB annotations RSQB
                     | name COLON name
                     | name'''
        if (len(p) == 7):
            name = p[1]
            typename = p[3]
            p[0] = ast.Parameter(name, typename)
        elif (len(p) == 4):
            name = p[1]
            typename = p[3]
            p[0] = ast.Parameter(name, typename)
        elif (len(p) == 2):
            name = p[1]
            p[0] = ast.Parameter(name)

    def p_statement_break(self, p):
        '''statement : BREAK SEMI'''
        p[0] = ast.Break(p[1])

    def p_statement_continue(self, p):
        '''statement : CONTINUE SEMI'''
        p[0] = ast.Continue(p[1])

    def p_statement_return(self, p):
        '''statement : RETURN expression SEMI'''
        p[0] = ast.Return(p[2])

    def p_statement_expression(self, p):
        '''statement : expression SEMI'''
        p[0] = p[1]

    def p_expression_or(self, p):
        '''expression : expression OR expression'''
        p[0] = ast.Or(p[1], p[3])

    def p_expression_and(self, p):
        '''expression : expression AND expression'''
        p[0] = ast.And(p[1], p[3])

    def p_exrepssion_not(self, p):
        '''expression : NOT expression'''
        p[0] = ast.Not(p[2])

    def p_expression_relationalop(self, p):
        '''expression : expression EQEQUAL expression
                      | expression NOTEQUAL expression
                      | expression LESS expression
                      | expression LESSEQUAL expression
                      | expression GREATER expression
                      | expression GREATEREQUAL expression'''
        left = p[1]
        right = p[3]
        operator = token.NAME[p[2]]
        if (operator == token.EQEQUAL):
            p[0] = ast.EqEqual(left, right)
        elif (operator == token.NOTEQUAL):
            p[0] = ast.NotEqual(left, right)
        elif (operator == token.LESS):
            p[0] = ast.Less(left, right)
        elif (operator == token.LESSEQUAL):
            p[0] = ast.LessEqual(left, right)
        elif (operator == token.GREATER):
            p[0] = ast.Greater(left, right)
        elif (operator == token.GREATEREQUAL):
            p[0] = ast.GreaterEqual(left, right)
    
    def p_expression_binaryop(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression STAR expression
                      | expression DOUBLESTAR expression
                      | expression SLASH expression
                      | expression DOUBLESLASH expression
                      | expression PERCENT expression'''
        left = p[1]
        right = p[3]
        operator = token.NAME[p[2]]
        if (operator == token.PLUS):
            p[0] = ast.Plus(left, right)
        elif (operator == token.MINUS):
            p[0] = ast.Minus(left, right)
        elif (operator == token.STAR):
            p[0] = ast.Star(left, right)
        elif (operator == token.DOUBLESTAR):
            p[0] = ast.DoubleStar(left, right)
        elif (operator == token.SLASH):
            p[0] = ast.Slash(left, right)
        elif (operator == token.DOUBLESLASH):
            p[0] = ast.DoubleSlash(left, right)
        elif (operator == token.PERCENT):
            p[0] = ast.Percent(left, right)

    def p_expression_unaryop(self, p):
        '''expression : PLUS expression %prec UPLUS
                      | MINUS expression %prec UMINUS'''
        right = p[2]
        operator = token.NAME[p[1]]
        if (operator == token.PLUS):
            p[0] = ast.UPlus(right)
        elif (operator == token.MINUS):
            p[0] = ast.UMinus(right)

    def p_expression_group(self, p):
        '''expression : LPAR expression RPAR'''
        p[0] = p[2]

    def p_expression_dotname(self, p):
        '''expression : expression DOT name'''
        # TODO
        pass

    def p_expression_call(self, p):
        '''expression : expression LPAR arguments RPAR
                      | expression LPAR RPAR'''
        if (len(p) == 5):
            expression = p[1]
            arguments = p[3]
            p[0] = ast.Call(expression, arguments)
        elif (len(p) == 4):
            expression = p[1]
            arguments = []
            p[0] = ast.Call(expression, arguments)

    def p_arguments(self, p):
        '''arguments : args COMMA
                     | args'''
        p[0] = p[1] 

    def p_args(self, p):
        '''args : args COMMA expression
                | expression'''
        if (len(p) == 4):
            args = p[1]
            expression = p[3]
            if (expression): args.append(expression)
            p[0] = args
        elif (len(p) == 2):
            expression = p[1]
            p[0] = list([expression])

    def p_expression_atom(self, p):
        '''expression : true
                      | false
                      | null
                      | name
                      | integer
                      | float
                      | complex
                      | string
                      | tuple
                      | list
                      | dict'''
        p[0] = p[1]

    def p_true(self, p):
        '''true : TRUE'''
        p[0] = ast.Boolean(True)

    def p_false(self, p):
        '''false : FALSE'''
        p[0] = ast.Boolean(False)

    def p_null(self, p):
        '''null : NULL'''
        p[0] = ast.Null(p[1])

    def p_name(self, p):
        '''name : NAME'''
        p[0] = ast.Name(p[1])

    def p_integer(self, p):
        '''integer : INTEGER'''
        p[0] = ast.Integer(p[1])

    def p_float(self, p):
        '''float : FLOAT'''
        p[0] = ast.Float(p[1])

    def p_complex(self, p):
        '''complex : COMPLEX'''
        p[0] = ast.Complex(p[1])

    def p_string(self, p):
        '''string : STRING'''
        p[0] = ast.String(p[1])

    def p_tuple(self, p):
        '''tuple : LPAR expression COMMA expressions RPAR
                 | LPAR expression COMMA RPAR
                 | LPAR RPAR'''
        if (len(p) == 6):
            expression = p[2]
            expressions = p[4]
            p[0] = ast.Tuple(list([expression] + expressions))
        elif (len(p) == 5):
            expression = p[2]
            p[0] = ast.Tuple(list([expression]))
        elif (len(p) == 3):
            p[0] = ast.Tuple(list())

    def p_list(self, p):
        '''list : LSQB expressions RSQB
                | LSQB RSQB'''
        if (len(p) == 4):
            expressions = p[2]
            p[0] = ast.List(expressions)
        elif (len(p) == 3):
            p[0] = ast.List(list())

    def p_dict(self, p):
        '''dict : LBRACE kvpairs RBRACE
                | LBRACE RBRACE'''
        if (len(p) == 4):
            kvpairs = p[2]
            p[0] = ast.Dict(kvpairs)
        elif (len(p) == 3):
            p[0] = ast.Dict(list())

    def p_expressions(self, p):
        '''expressions : _expressions COMMA
                       | _expressions'''
        p[0] = p[1] 

    def p__expressions(self, p):
        '''_expressions : _expressions COMMA expression
                        | expression'''
        if (len(p) == 4):
            expressions = p[1]
            expression = p[3]
            if (expression): expressions.append(expression)
            p[0] = expressions
        elif (len(p) == 2):
            expression = p[1]
            p[0] = list([expression])

    def p_kvpairs(self, p):
        '''kvpairs : _kvpairs COMMA
                   | _kvpairs'''
        p[0] = p[1]

    def p__kvpairs(self, p):
        '''_kvpairs : _kvpairs COMMA kvpair
                    | kvpair'''
        if (len(p) == 4):
            kvpairs = p[1]
            kvpair = p[3]
            if (kvpair): kvpairs.append(kvpair)
            p[0] = kvpairs
        elif (len(p) == 2):
            kvpair = p[1]
            p[0] = list([kvpair])

    def p_kvpair(self, p):
        '''kvpair : expression COLON expression'''
        key = p[1]
        value = p[3]
        p[0] = tuple((key, value,))

    def p_empty(self, p):
        '''empty : '''
        pass

    def p_error(self, p):
        system.GLOBAL.log.debug(f'Error: {p}')
        pass
