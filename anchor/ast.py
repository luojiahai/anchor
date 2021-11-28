import abc
import anchor.builtins as builtins
import anchor.symtable as symtable


class ASTNode(abc.ABC):

    @abc.abstractmethod
    def evaluate(self, st): pass


class Program(ASTNode):

    def __init__(self, block):
        self.__block = block

    @property
    def block(self):
        return self.__block
    
    def evaluate(self, st):
        return self.block.evaluate(st)


class Block(ASTNode):

    def __init__(self, statements):
        self.__statements = statements

    @property
    def statements(self):
        return self.__statements

    def evaluate(self, st):
        for statement in self.statements:
            statement.evaluate(st)
        return None


class Statement(ASTNode): pass


class Terminal(Statement): pass


class Assignment(Statement):

    def __init__(self, name, expression):
        self.__name = name
        self.__expression = expression

    @property
    def name(self):
        return self.__name

    @property
    def expression(self):
        return self.__expression

    def evaluate(self, st):
        identifier = self.name.identifier
        flags = dict()
        namespaces = list([self.expression.evaluate(st)])
        st.insert(identifier, flags, namespaces)
        return None


class If(Statement):

    def __init__(self, expression, block, elif_statements=list(), else_block=None):
        self.__expression = expression
        self.__block = block
        self.__elif_statements = elif_statements
        self.__else_block = else_block

    @property
    def expression(self):
        return self.__expression
    
    @property
    def block(self):
        return self.__block

    @property
    def elif_statements(self):
        return self.__elif_statements

    @property
    def else_block(self):
        return self.__else_block

    def evaluate(self, st):
        if (self.expression.evaluate(st)):
            return self.block.evaluate(st)
        else:
            for elif_statement in self.elif_statements:
                if (elif_statement.expression.evaluate(st)):
                    return elif_statement.evaluate(st)
                elif (elif_statement.else_block):
                    return elif_statement.else_block.evaluate(st)
            
            if (self.else_block):
                return self.else_block.evaluate(st)
            return None


class Elif(Statement):

    def __init__(self, expression, block, else_block=None):
        self.__expression = expression
        self.__block = block
        self.__else_block = else_block

    @property
    def expression(self):
        return self.__expression
    
    @property
    def block(self):
        return self.__block

    @property
    def else_block(self):
        return self.__else_block

    def evaluate(self, st):
        return self.block.evaluate(st)


class FunctionDef(Statement):

    def __init__(self, name, parameters, body, default_args=list(), is_builtin=False):
        self.__name = name
        self.__parameters = parameters
        self.__body = body
        self.__default_args = default_args
        self.__is_builtin = is_builtin

    @property
    def name(self):
        return self.__name

    @property
    def parameters(self):
        return self.__parameters

    @property
    def body(self):
        return self.__body

    @property
    def default_args(self):
        return self.__default_args

    @property
    def is_builtin(self):
        return self.__is_builtin

    def evaluate(self, st):
        identifier = self.name.identifier
        flags = dict({'is_namespace': True})
        namespaces = list([self])
        st.insert(identifier, flags, namespaces)
        return None


class Return(Terminal):

    def __init__(self, expression):
        self.__expression = expression

    @property
    def expression(self):
        return self.__expression

    def evaluate(self, st):
        return self.expression.evaluate(st)


class Expression(ASTNode): pass


class Or(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left or right
        return builtins.TYPE[type(value).__name__](value)


class And(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left and right
        return builtins.TYPE[type(value).__name__](value)


class Not(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = not right
        return builtins.TYPE[type(value).__name__](value)


class EqEqual(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left == right
        return builtins.TYPE[type(value).__name__](value)


class NotEqual(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left != right
        return builtins.TYPE[type(value).__name__](value)


class Less(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left < right
        return builtins.TYPE[type(value).__name__](value)


class LessEqual(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left <= right
        return builtins.TYPE[type(value).__name__](value)


class Greater(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left > right
        return builtins.TYPE[type(value).__name__](value)


class GreaterEqual(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left >= right
        return builtins.TYPE[type(value).__name__](value)


class Plus(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left + right
        return builtins.TYPE[type(value).__name__](value)


class Minus(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left - right
        return builtins.TYPE[type(value).__name__](value)


class Star(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left * right
        return builtins.TYPE[type(value).__name__](value)


class DoubleStar(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left ** right
        return builtins.TYPE[type(value).__name__](value)


class Slash(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left / right
        return builtins.TYPE[type(value).__name__](value)


class DoubleSlash(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left // right
        return builtins.TYPE[type(value).__name__](value)


class Percent(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        left = self.left.evaluate(st)
        right = self.right.evaluate(st)
        value = left % right
        return builtins.TYPE[type(value).__name__](value)


class UPlus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = +right
        return builtins.TYPE[type(value).__name__](value)


class UMinus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = -right
        return builtins.TYPE[type(value).__name__](value)


class Name(Expression):

    def __init__(self, identifier):
        self.__identifier = identifier

    @property
    def identifier(self):
        return self.__identifier

    def evaluate(self, st):
        symbol = st.lookup(self.identifier)
        if (not symbol):
            raise NameError()
        return symbol.namespace


class Boolean(Expression):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        return builtins.Boolean(bool(self.value))


class Null(Expression):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        return builtins.Null(self.value)


class String(Expression):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        return builtins.String(str(self.value[1:-1]))


class Integer(Expression):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        return builtins.Integer(int(self.value))


class Float(Expression):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        return builtins.Float(float(self.value))


class Complex(Expression):

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        return builtins.Complex(complex(self.value))


class Tuple(Expression):

    def __init__(self, expressions):
        self._expressions = expressions

    @property
    def expressions(self):
        return self._expressions
    
    def evaluate(self, st):
        return builtins.Tuple(tuple([
            expression.evaluate(st) 
            for expression in self.expressions
        ]))


class List(Expression):

    def __init__(self, expressions):
        self._expressions = expressions

    @property
    def expressions(self):
        return self._expressions
    
    def evaluate(self, st):
        return builtins.List(list([
            expression.evaluate(st) 
            for expression in self.expressions
        ]))


class Dict(Expression):

    def __init__(self, kvpairs):
        self._kvpairs = kvpairs

    @property
    def kvpairs(self):
        return self._kvpairs

    def evaluate(self, st):
        the_dict = dict()
        for k, v in self.kvpairs:
            key = k.evaluate(st)
            value = v.evaluate(st)
            the_dict[key] = value
        return builtins.Dict(the_dict)


class Call(Expression):

    def __init__(self, name, arguments):
        self.__name = name
        self.__arguments = arguments

    @property
    def name(self):
        return self.__name

    @property
    def arguments(self):
        return self.__arguments
    
    def evaluate(self, st):
        # Get function definition and its attributes
        identifier = self.name.identifier
        functiondef = st.lookup(identifier).namespace
        parameters = functiondef.parameters
        body = functiondef.body

        # Create function symbol table
        function_symtable = symtable.Function(identifier, st)

        # Insert symbols for arguments
        for index in range(len(parameters)):
            parameter = parameters[index]
            identifier = parameter.identifier
            flags = dict({'is_parameter': True})
            namespaces = list([
                self.arguments[index].evaluate(st)
                if index < len(self.arguments)
                else functiondef.default_args[identifier]
            ])
            function_symtable.insert(identifier, flags, namespaces)
        
        # Evaluate function body
        if (functiondef.is_builtin):
            function = body
            args = dict()
            for parameter in parameters:
                value = parameter.evaluate(function_symtable)
                args[parameter.identifier] = value
            value = function(**args)
            return builtins.TYPE[type(value).__name__](value)
        else:
            # Case: user-defined function
            pass


# Anchor builtin type name to AST node
TYPE_NODE = {
    'Boolean': Boolean,
    'Null': Null,
    'Integer': Integer,
    'Float': Float,
    'Complex': Complex,
    'String': String,
    'Tuple': Tuple,
    'List': List,
    'Dict': Dict,
}
