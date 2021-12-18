import typing
import abc
import anchor.ply.yacc as yacc
import anchor.lex as lex
import anchor.token as token
import anchor.ast as ast
import anchor.system as system


__all__: typing.List[str] = list(['AnchorParser',])


class Parser(abc.ABC):

    tokens: typing.Tuple = tuple()
    precedence: typing.Tuple = tuple()

    def __init__(self, **kwargs) -> None:
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
    tokens: typing.Tuple = lex.AnchorLexer.tokens

    # Precedence rules
    precedence: typing.Tuple = tuple((
        ('left', token.OR,),
        ('left', token.AND,),
        ('right', token.NOT,),
        ('nonassoc', token.EQEQUAL, token.NOTEQUAL, 
            token.LESS, token.GREATER, token.LESSEQUAL, token.GREATEREQUAL,),
        ('left', token.PLUS, token.MINUS,),
        ('left', token.STAR, token.SLASH, token.DOUBLESLASH, token.PERCENT,),
        ('right', token.UPLUS, token.UMINUS,),
        ('left', token.DOUBLESTAR,),
        ('left', token.LPAR, token.RPAR,),
    ))

    def p_program(self, p: yacc.YaccProduction) -> None:
        '''program : block
                   | empty'''
        if (p[1]):
            block: ast.Block = p[1]
            p[0] = ast.Program(block)

    def p_block(self, p: yacc.YaccProduction) -> None:
        '''block : statements'''
        statements: typing.List[ast.Statement] = p[1]
        p[0] = ast.Block(statements)

    def p_statements(self, p: yacc.YaccProduction) -> None:
        '''statements : statements statement
                      | statement'''
        if (len(p) == 3):
            statements: typing.List[ast.Statement] = p[1]
            statement: ast.Statement = p[2]
            if (statement): statements.append(statement)
            p[0] = statements
        elif (len(p) == 2):
            statement: ast.Statement = p[1]
            p[0] = list([statement])

    def p_statement_assignment(self, p: yacc.YaccProduction) -> None:
        '''statement : name EQUAL expression SEMI'''
        name: ast.Name = p[1]
        expression: ast.Expression = p[3]
        p[0] = ast.Assignment(name, expression)

    def p_statement_if(self, p: yacc.YaccProduction) -> None:
        '''statement : IF expression THEN block elifs END'''
        expression: ast.Expression = p[2]
        block: ast.Block = p[4]
        elifs: typing.List[ast.Elif] = p[5]
        p[0] = ast.If(expression, block, elifs=elifs)

    def p_statement_ifelse(self, p: yacc.YaccProduction) -> None:
        '''statement : IF expression THEN block elseblock END
                     | IF expression THEN block END'''
        if (len(p) == 7):
            expression: ast.Expression = p[2]
            block: ast.Block = p[4]
            elseblock: ast.Block = p[5]
            p[0] = ast.If(expression, block, elseblock=elseblock)
        elif (len(p) == 6):
            expression: ast.Expression = p[2]
            block: ast.Block = p[4]
            p[0] = ast.If(expression, block)

    def p_elifs(self, p: yacc.YaccProduction) -> None:
        '''elifs : ELIF expression THEN block elifs'''
        expression: ast.Expression = p[2]
        block: ast.Block = p[4]
        elifs: typing.List[ast.Elif] = p[5]
        p[0] = list([ast.Elif(expression, block)]) + elifs

    def p_elifs_else(self, p: yacc.YaccProduction) -> None:
        '''elifs : ELIF expression THEN block elseblock
                 | ELIF expression THEN block'''
        if (len(p) == 6):
            expression: ast.Expression = p[2]
            block: ast.Block = p[4]
            elseblock: ast.Block = p[5]
            p[0] = list([ast.Elif(expression, block, elseblock)])
        elif (len(p) == 5):
            expression: ast.Expression = p[2]
            block: ast.Block = p[4]
            p[0] = list([ast.Elif(expression, block)])

    def p_elseblock(self, p: yacc.YaccProduction) -> None:
        '''elseblock : ELSE block'''
        block: ast.Block = p[2]
        p[0] = block

    def p_statement_iterate(self, p: yacc.YaccProduction) -> None:
        '''statement : ITERATE expression FOR name BEGIN block END'''
        iterable: ast.Expression = p[2]
        variable: ast.Name = p[4]
        block: ast.Block = p[6]
        p[0] = ast.Iterate(iterable, variable, block)

    def p_statement_loop(self, p: yacc.YaccProduction) -> None:
        '''statement : LOOP expression BEGIN block END'''
        expression: ast.Expression = p[2]
        block: ast.Block = p[4]
        p[0] = ast.Loop(expression, block)

    def p_statement_functiondef(self, p: yacc.YaccProduction) -> None:
        '''statement : FUNCTION name LPAR parameters RPAR \
                       RARROW expression BEGIN block END
                     | FUNCTION name LPAR RPAR \
                       RARROW expression BEGIN block END'''
        if (len(p) == 11):
            name: ast.Name = p[2]
            parameters: typing.List[ast.Parameter] = p[4]
            returntype: ast.Expression = p[7]
            body: ast.Block = p[9]
            p[0] = ast.FunctionDef(
                name, parameters, body, returntype=returntype
            )
        elif (len(p) == 10):
            name: ast.Name = p[2]
            parameters: typing.List[ast.Parameter] = list()
            returntype: ast.Expression = p[7]
            body: ast.Block = p[8]
            p[0] = ast.FunctionDef(
                name, parameters, body, returntype=returntype
            )

    def p_statement_classdef(self, p: yacc.YaccProduction) -> None:
        '''statement : CLASS LSQB annotations RSQB name BEGIN block END'''
        annotations: typing.List[ast.Annotation] = p[3]
        name: ast.Name = p[5]
        block: ast.Block = p[7]
        p[0] = ast.ClassDef(name, block, annotations)

    def p_statement_property(self, p: yacc.YaccProduction) -> None:
        '''statement : PROPERTY LSQB annotations RSQB name SEMI'''
        annotations: typing.List[ast.Annotation] = p[3]
        name: ast.Name = p[5]
        p[0] = ast.Property(name, annotations)

    def p_statement_methoddef(self, p: yacc.YaccProduction) -> None:
        '''statement : METHOD LSQB annotations RSQB name LPAR parameters RPAR \
                       RARROW expression BEGIN block END
                     | METHOD LSQB annotations RSQB name LPAR RPAR \
                       RARROW expression BEGIN block END'''
        if (len(p) == 14):
            annotations: typing.List[ast.Annotation] = [p[3]]
            name: ast.Name = p[5]
            parameters: typing.List[ast.Parameter] = p[7]
            returntype: ast.Expression = p[10]
            body: ast.Block = p[12]
            p[0] = ast.MethodDef(
                name, parameters, body, annotations, returntype=returntype
            )
        elif (len(p) == 13):
            annotations: typing.List[ast.Annotation] = [p[3]]
            name: ast.Name = p[5]
            parameters: typing.List[ast.Parameter] = []
            returntype: ast.Expression = p[9]
            body: ast.Block = p[11]
            p[0] = ast.MethodDef(
                name, parameters, body, annotations, returntype=returntype
            )

    def p_annotations(self, p: yacc.YaccProduction) -> None:
        '''annotations : annotations_ COMMA
                       | annotations_'''
        p[0] = p[1] 

    def p_annotations_(self, p: yacc.YaccProduction) -> None:
        '''annotations_ : annotations_ COMMA annotation
                        | annotation'''
        if (len(p) == 4):
            annotations: typing.List[ast.Annotation] = p[1]
            annotation: ast.Annotation = p[3]
            if (annotation): annotations.append(annotation)
            p[0] = annotations
        elif (len(p) == 2):
            annotation: ast.Annotation = p[1]
            p[0] = list([annotation])

    def p_annotation(self, p: yacc.YaccProduction) -> None:
        '''annotation : PUBLIC
                      | PRIVATE
                      | PROTECTED
                      | FACTORY
                      | GET
                      | SET
                      | REF
                      | VAL'''
        literal: str = p[1]
        p[0] = ast.Annotation(literal)

    def p_parameters(self, p: yacc.YaccProduction) -> None:
        '''parameters : parameters_ COMMA
                      | parameters_'''
        p[0] = p[1] 

    def p_parameters_(self, p: yacc.YaccProduction) -> None:
        '''parameters_ : parameters_ COMMA parameter
                       | parameter'''
        if (len(p) == 4):
            parameters: typing.List[ast.Parameter] = p[1]
            parameter: ast.Parameter = p[3]
            if (parameter): parameters.append(parameter)
            p[0] = parameters
        if (len(p) == 2):
            parameter: ast.Parameter = p[1]
            p[0] = list([parameter])

    def p_parameter(self, p: yacc.YaccProduction) -> None:
        '''parameter : name COLON name LSQB annotations RSQB
                     | name COLON name
                     | name'''
        if (len(p) == 7):
            name: ast.Name = p[1]
            typename: ast.Name = p[3]
            p[0] = ast.Parameter(name, typename)
        elif (len(p) == 4):
            name: ast.Name = p[1]
            typename: ast.Name = p[3]
            p[0] = ast.Parameter(name, typename)
        elif (len(p) == 2):
            name: ast.Name = p[1]
            p[0] = ast.Parameter(name)

    def p_statement_break(self, p: yacc.YaccProduction) -> None:
        '''statement : BREAK SEMI'''
        p[0] = ast.Break(literal=p[1])

    def p_statement_continue(self, p: yacc.YaccProduction) -> None:
        '''statement : CONTINUE SEMI'''
        p[0] = ast.Continue(literal=p[1])

    def p_statement_return(self, p: yacc.YaccProduction) -> None:
        '''statement : RETURN expression SEMI'''
        expression = p[2]
        p[0] = ast.Return(expression=expression)

    def p_statement_expression(self, p: yacc.YaccProduction) -> None:
        '''statement : expression SEMI'''
        p[0] = p[1]

    def p_expression_or(self, p: yacc.YaccProduction) -> None:
        '''expression : expression OR expression'''
        p[0] = ast.Or(p[1], p[3])

    def p_expression_and(self, p: yacc.YaccProduction) -> None:
        '''expression : expression AND expression'''
        p[0] = ast.And(p[1], p[3])

    def p_exrepssion_not(self, p: yacc.YaccProduction) -> None:
        '''expression : NOT expression'''
        p[0] = ast.Not(p[2])

    def p_expression_relationalop(self, p: yacc.YaccProduction) -> None:
        '''expression : expression EQEQUAL expression
                      | expression NOTEQUAL expression
                      | expression LESS expression
                      | expression LESSEQUAL expression
                      | expression GREATER expression
                      | expression GREATEREQUAL expression'''
        left: ast.Expression = p[1]
        right: ast.Expression = p[3]
        operator: str = token.NAME[p[2]]
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
    
    def p_expression_binaryop(self, p: yacc.YaccProduction) -> None:
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression STAR expression
                      | expression DOUBLESTAR expression
                      | expression SLASH expression
                      | expression DOUBLESLASH expression
                      | expression PERCENT expression'''
        left: ast.Expression = p[1]
        right: ast.Expression = p[3]
        operator: str = token.NAME[p[2]]
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

    def p_expression_unaryop(self, p: yacc.YaccProduction) -> None:
        '''expression : PLUS expression %prec UPLUS
                      | MINUS expression %prec UMINUS'''
        right: ast.Expression = p[2]
        operator: str = token.NAME[p[1]]
        if (operator == token.PLUS):
            p[0] = ast.UPlus(right)
        elif (operator == token.MINUS):
            p[0] = ast.UMinus(right)

    def p_expression_group(self, p: yacc.YaccProduction) -> None:
        '''expression : LPAR expression RPAR'''
        p[0] = p[2]

    def p_expression_dotname(self, p: yacc.YaccProduction) -> None:
        '''expression : expression DOT name'''
        expression = p[1]
        name = p[3]
        p[0] = ast.DotName(expression, name)

    def p_expression_call(self, p: yacc.YaccProduction) -> None:
        '''expression : expression LPAR arguments RPAR
                      | expression LPAR RPAR'''
        if (len(p) == 5):
            expression: ast.Expression = p[1]
            arguments: typing.List[ast.Expression] = p[3]
            p[0] = ast.Call(expression, arguments)
        elif (len(p) == 4):
            expression: ast.Expression = p[1]
            arguments: typing.List[ast.Expression] = []
            p[0] = ast.Call(expression, arguments)

    def p_arguments(self, p: yacc.YaccProduction) -> None:
        '''arguments : args COMMA
                     | args'''
        p[0] = p[1] 

    def p_args(self, p: yacc.YaccProduction) -> None:
        '''args : args COMMA expression
                | expression'''
        if (len(p) == 4):
            args: typing.List[ast.Expression] = p[1]
            expression: ast.Expression = p[3]
            if (expression): args.append(expression)
            p[0] = args
        elif (len(p) == 2):
            expression: ast.Expression = p[1]
            p[0] = list([expression])

    def p_expression_atom(self, p: yacc.YaccProduction) -> None:
        '''expression : name
                      | true
                      | false
                      | null
                      | integer
                      | float
                      | complex
                      | string
                      | tuple
                      | list
                      | dict'''
        p[0] = p[1]

    def p_name(self, p: yacc.YaccProduction) -> None:
        '''name : NAME'''
        p[0] = ast.Name(p[1])

    def p_true(self, p: yacc.YaccProduction) -> None:
        '''true : TRUE'''
        p[0] = ast.Boolean(value=True)

    def p_false(self, p: yacc.YaccProduction) -> None:
        '''false : FALSE'''
        p[0] = ast.Boolean(value=False)

    def p_null(self, p: yacc.YaccProduction) -> None:
        '''null : NULL'''
        p[0] = ast.Null(literal=p[1])

    def p_integer(self, p: yacc.YaccProduction) -> None:
        '''integer : INTEGER'''
        p[0] = ast.Integer(literal=p[1])

    def p_float(self, p: yacc.YaccProduction) -> None:
        '''float : FLOAT'''
        p[0] = ast.Float(literal=p[1])

    def p_complex(self, p: yacc.YaccProduction) -> None:
        '''complex : COMPLEX'''
        p[0] = ast.Complex(literal=p[1])

    def p_string(self, p: yacc.YaccProduction) -> None:
        '''string : STRING'''
        p[0] = ast.String(literal=p[1])

    def p_tuple(self, p: yacc.YaccProduction) -> None:
        '''tuple : LPAR expression COMMA expressions RPAR
                 | LPAR expression COMMA RPAR
                 | LPAR RPAR'''
        if (len(p) == 6):
            expression: ast.Expression = p[2]
            expressions: typing.List[ast.Expression] = p[4]
            p[0] = ast.Tuple(expressions=list([expression] + expressions))
        elif (len(p) == 5):
            expression: ast.Expression = p[2]
            p[0] = ast.Tuple(expressions=list([expression]))
        elif (len(p) == 3):
            p[0] = ast.Tuple(expressions=list())

    def p_list(self, p: yacc.YaccProduction) -> None:
        '''list : LSQB expressions RSQB
                | LSQB RSQB'''
        if (len(p) == 4):
            expressions: typing.List[ast.Expression] = p[2]
            p[0] = ast.List(expressions=expressions)
        elif (len(p) == 3):
            p[0] = ast.List(expressions=list())

    def p_dict(self, p: yacc.YaccProduction) -> None:
        '''dict : LBRACE kvpairs RBRACE
                | LBRACE RBRACE'''
        if (len(p) == 4):
            kvpairs: typing.List[typing.Tuple[ast.Expression, ast.Expression]] \
                = p[2]
            p[0] = ast.Dict(kvpairs=kvpairs)
        elif (len(p) == 3):
            p[0] = ast.Dict(kvpairs=list())

    def p_expressions(self, p: yacc.YaccProduction) -> None:
        '''expressions : expressions_ COMMA
                       | expressions_'''
        p[0] = p[1] 

    def p_expressions_(self, p: yacc.YaccProduction) -> None:
        '''expressions_ : expressions_ COMMA expression
                        | expression'''
        if (len(p) == 4):
            expressions: typing.List[ast.Expression] = p[1]
            expression: ast.Expression = p[3]
            if (expression): expressions.append(expression)
            p[0] = expressions
        elif (len(p) == 2):
            expression: ast.Expression = p[1]
            p[0] = list([expression])

    def p_kvpairs(self, p: yacc.YaccProduction) -> None:
        '''kvpairs : kvpairs_ COMMA
                   | kvpairs_'''
        p[0] = p[1]

    def p_kvpairs_(self, p: yacc.YaccProduction) -> None:
        '''kvpairs_ : kvpairs_ COMMA kvpair
                    | kvpair'''
        if (len(p) == 4):
            kvpairs: typing.List[typing.Tuple[ast.Expression, ast.Expression]] \
                = p[1]
            kvpair: typing.Tuple[ast.Expression, ast.Expression] = p[3]
            if (kvpair): kvpairs.append(kvpair)
            p[0] = kvpairs
        elif (len(p) == 2):
            kvpair: typing.Tuple[ast.Expression, ast.Expression] = p[1]
            p[0] = list([kvpair])

    def p_kvpair(self, p: yacc.YaccProduction) -> None:
        '''kvpair : expression COLON expression'''
        key: ast.Expression = p[1]
        value: ast.Expression = p[3]
        p[0] = tuple((key, value,))

    def p_empty(self, p: yacc.YaccProduction) -> None:
        '''empty : '''
        p
        pass

    def p_error(self, p: yacc.YaccProduction) -> None:
        system.GLOBAL.logger.debug(f'Error: {p}')
        pass
