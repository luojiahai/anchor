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
        value, _ = self.block.evaluate(st)
        return value


class Block(ASTNode):

    def __init__(self, statements):
        self.__statements = statements

    @property
    def statements(self):
        return self.__statements

    def evaluate(self, st):
        for statement in self.statements:
            value = statement.evaluate(st)
            if (isinstance(value, Return)):
                return (value.expression.evaluate(st), {'return': True},)
            elif (isinstance(value, Break)):
                return (value, {'break': True},)
            elif (isinstance(value, Continue)):
                return (value, {'continue': True},)
        return (None, {},)


class Statement(ASTNode): pass


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
        namespaces = list([self.expression.evaluate(st)])
        st.insert(identifier, namespaces)
        return None


class If(Statement):

    def __init__(
        self, expression, block, 
        elif_statements=list(), else_block=None
    ):
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


class Iterate(Statement):

    def __init__(self, iterable, variable, block):
        self.__iterable = iterable
        self.__variable = variable
        self.__block = block

    @property
    def iterable(self):
        return self.__iterable
    
    @property
    def variable(self):
        return self.__variable

    @property
    def block(self):
        return self.__block

    def evaluate(self, st):
        identifier = self.variable.identifier
        for e in self.iterable.evaluate(st):
            namespaces = list([e])
            st.insert(identifier, namespaces)
            value, flags = self.block.evaluate(st)
            if (flags.get('return', False)):
                return value
            elif (flags.get('break', False)):
                break
            elif (flags.get('continue', False)):
                continue
        return None


class Loop(Statement):

    def __init__(self, expression, block):
        self.__expression = expression
        self.__block = block

    @property
    def expression(self):
        return self.__expression
    
    @property
    def block(self):
        return self.__block

    def evaluate(self, st):
        while (self.expression.evaluate(st)):
            value, flags = self.block.evaluate(st)
            if (flags.get('return', False)):
                return value
            elif (flags.get('break', False)):
                break
            elif (flags.get('continue', False)):
                continue
        return None


class Break(Statement):

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    def evaluate(self, st):
        return self


class Continue(Statement):
    
    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    def evaluate(self, st):
        return self


class FunctionDef(Statement):

    def __init__(self, name, parameters, body, **flags):
        self.__name = name
        self.__parameters = parameters
        self.__body = body
        self.__flags = flags

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
    def flags(self):
        return self.__flags

    def evaluate(self, st):
        identifier = self.name.identifier
        fn = builtins.Function(self.name, self.parameters, self.body, **self.flags)
        namespaces = list([fn])
        st.insert(identifier, namespaces, isnamespace=True)
        return None


class ClassDef(Statement):

    def __init__(self, name, superclasses, block, **flags):
        self.__name = name
        self.__superclasses = superclasses
        self.__block = block
        self.__flags = flags

        self.__properties = dict()
        self.__methods = dict()
        for statement in self.__block.statements:
            if (isinstance(statement, Property)):
                identifier = statement.name.identifier
                self.__properties[identifier] = statement
            elif (isinstance(statement, FunctionDef)):
                identifier = statement.name.identifier
                self.__methods[identifier] = statement

        if ('init' not in self.__methods):
            name = Name('init')
            parameters = list()
            body = Block(list())
            self.__methods['init'] = FunctionDef(name, parameters, body)

    @property
    def name(self):
        return self.__name

    @property
    def superclasses(self):
        return self.__superclasses

    @property
    def block(self):
        return self.__block

    @property
    def flags(self):
        return self.__flags

    @property
    def properties(self):
        return self.__properties

    @property
    def methods(self):
        return self.__methods

    def evaluate(self, st):
        identifier = self.name.identifier
        cs = builtins.Class(self.name, self.superclasses, self.properties, self.methods, **self.flags)
        namespaces = list([cs])
        st.insert(identifier, namespaces, isnamespace=True)
        return None


class Property(Statement):

    def __init__(self, name):
        self.__name = name

    @property
    def name(self):
        return self.__name


class Return(Statement):

    def __init__(self, expression):
        self.__expression = expression

    @property
    def expression(self):
        return self.__expression

    def evaluate(self, st):
        return self


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


class Not(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = not right
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


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
        return TYPE[type(value)](value)


class UPlus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = +right
        return TYPE[type(value)](value)


class UMinus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = -right
        return TYPE[type(value)](value)


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
        return builtins.String(str(self.value))


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
        self.__expressions = expressions

    @property
    def expressions(self):
        return self.__expressions
    
    def evaluate(self, st):
        return builtins.Tuple(tuple([
            expression.evaluate(st) 
            for expression in self.expressions
        ]))


class List(Expression):

    def __init__(self, expressions):
        self.__expressions = expressions

    @property
    def expressions(self):
        return self.__expressions
    
    def evaluate(self, st):
        return builtins.List(list([
            expression.evaluate(st) 
            for expression in self.expressions
        ]))


class Dict(Expression):

    def __init__(self, kvpairs):
        self.__kvpairs = kvpairs

    @property
    def kvpairs(self):
        return self.__kvpairs

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
        namespace = st.lookup(identifier).namespace

        if (isinstance(namespace, builtins.Class)):
            cs = namespace
            superclasses = cs.superclasses
            properties = cs.properties
            methods = cs.methods
            csst = symtable.Class(identifier, st)

            # TODO: Insert symbols for properties
            # TODO: Insert methods for properties

            # Evaluate constructor
            constructor = methods['init']
            constructor.evaluate(csst)
            call = Call(Name('init'), self.arguments)
            call.evaluate(csst)

            # Return class instance
            return builtins.Object(identifier, csst)

        elif (isinstance(namespace, builtins.Function)):
            fn = namespace
            parameters = fn.parameters
            body = fn.body
            fnst = symtable.Function(identifier, st)

            # Insert symbols for arguments
            for index in range(len(parameters)):
                parameter = parameters[index]
                identifier = parameter.identifier
                namespaces = list([self.arguments[index].evaluate(st)])
                fnst.insert(identifier, namespaces, isparameter=True)
            
            # Evaluate function body
            if (fn.flags.get('isbuiltin', False)):
                fnptr = body
                args = dict()
                for parameter in parameters:
                    value = parameter.evaluate(fnst)
                    args[parameter.identifier] = value
                value = fnptr(**args)
                return TYPE[type(value)](value)
            else:
                block = body
                value, _ = block.evaluate(fnst)
                return value


TYPE = {
    bool: builtins.Boolean,
    type(None): builtins.Null,
    int: builtins.Integer,
    float: builtins.Float,
    complex: builtins.Complex,
    str: builtins.String,
    tuple: builtins.Tuple,
    list: builtins.List,
    dict: builtins.Dict,
}
