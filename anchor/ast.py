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
        node = self.block.evaluate(st)
        return node


class Block(ASTNode):

    def __init__(self, statements):
        self.__statements = statements

    @property
    def statements(self):
        return self.__statements

    def evaluate(self, st):
        for statement in self.statements:
            node = statement.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                return node
            elif (isinstance(node, Continue)):
                return node
        return None


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
        if (self.expression.evaluate(st).value):
            return self.block.evaluate(st)
        else:
            for elif_statement in self.elif_statements:
                if (elif_statement.expression.evaluate(st).value):
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
        for e in self.iterable.evaluate(st).iterable:
            namespaces = list([e])
            st.insert(identifier, namespaces)
            node = self.block.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                break
            elif (isinstance(node, Continue)):
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
        while (self.expression.evaluate(st).value):
            node = self.block.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                break
            elif (isinstance(node, Continue)):
                continue
        return None


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


class Return(Statement):

    __value = None

    def __init__(self, expression):
        self.__expression = expression

    @property
    def expression(self):
        return self.__expression

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = self.expression.evaluate(st).value
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
        value = left.value or right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value and right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Not(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = not right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value == right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value != right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value < right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value <= right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value > right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value >= right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value + right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value - right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value * right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value ** right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value / right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value // right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


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
        value = left.value % right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class UPlus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = +right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class UMinus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self):
        return self.__right

    def evaluate(self, st):
        right = self.right.evaluate(st)
        value = -right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Name(Expression):

    def __init__(self, identifier):
        self.__identifier = identifier

    @property
    def identifier(self):
        return self.__identifier

    def evaluate(self, st):
        symbol = st.lookup(self.identifier)
        return symbol.namespace


class Boolean(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = builtins.Boolean(bool(self.literal))
        return self


class Null(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = builtins.Null(self.literal)
        return self


class String(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = builtins.String(str(self.literal))
        return self


class Integer(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = builtins.Integer(int(self.literal))
        return self


class Float(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = builtins.Float(float(self.literal))
        return self


class Complex(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self):
        return self.__value

    def evaluate(self, st):
        self.__value = builtins.Complex(complex(self.literal))
        return self


class Tuple(Expression):

    __value = None
    __iterable = None

    def __init__(self, expressions):
        self.__expressions = expressions

    @property
    def expressions(self):
        return self.__expressions

    @property
    def value(self):
        return self.__value

    @property
    def iterable(self):
        return self.__iterable
    
    def evaluate(self, st):
        self.__value = builtins.Tuple(tuple([
            expression.evaluate(st).value
            for expression in self.expressions
        ]))
        self.__iterable = tuple([
            expression.evaluate(st)
            for expression in self.expressions
        ])
        return self


class List(Expression):

    __value = None
    __iterable = None

    def __init__(self, expressions):
        self.__expressions = expressions

    @property
    def expressions(self):
        return self.__expressions

    @property
    def value(self):
        return self.__value

    @property
    def iterable(self):
        return self.__iterable
    
    def evaluate(self, st):
        self.__value = builtins.List(list([
            expression.evaluate(st).value
            for expression in self.expressions
        ]))
        self.__iterable = list([
            expression.evaluate(st) 
            for expression in self.expressions
        ])
        return self


class Dict(Expression):

    __value = None
    __iterable = None

    def __init__(self, kvpairs):
        self.__kvpairs = kvpairs

    @property
    def kvpairs(self):
        return self.__kvpairs

    @property
    def value(self):
        return self.__value

    @property
    def iterable(self):
        return self.__iterable

    def evaluate(self, st):
        self.__value = builtins.Dict({
            k.evaluate(st).value: v.evaluate(st).value
            for k, v in self.kvpairs
        })
        self.__iterable = dict({
            k.evaluate(st): v.evaluate(st)
            for k, v in self.kvpairs
        })
        return self


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
                    value = parameter.evaluate(fnst).value
                    args[parameter.identifier] = value
                value = fnptr(**args)
                return TYPE[type(value)](value)
            else:
                block = body
                node = block.evaluate(fnst)
                return node


TYPE = {
    bool: Boolean,
    type(None): Null,
    int: Integer,
    float: Float,
    complex: Complex,
    str: String,
    tuple: Tuple,
    list: List,
    dict: Dict,
}
