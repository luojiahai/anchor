import abc
import typing
import anchor.builtins as builtins
import anchor.symtable as symtable


class ASTNode(abc.ABC):

    @abc.abstractmethod
    def evaluate(self, st): pass


class Expression(ASTNode): pass


class Statement(ASTNode): pass


class Block(ASTNode):

    def __init__(self, statements):
        self.__statements = statements

    @property
    def statements(self) -> list[Statement]:
        return self.__statements

    def evaluate(self, st) -> ASTNode:
        for statement in self.statements:
            node = statement.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                return node
            elif (isinstance(node, Continue)):
                return node
        return None


class Program(ASTNode):

    def __init__(self, block):
        self.__block = block

    @property
    def block(self) -> Block:
        return self.__block
    
    def evaluate(self, st) -> ASTNode:
        node = self.block.evaluate(st)
        return node


class Name(Expression):

    def __init__(self, identifier):
        self.__identifier = identifier

    @property
    def identifier(self) -> str:
        return self.__identifier

    def evaluate(self, st) -> ASTNode:
        symbol = st.lookup(self.identifier)
        return symbol.namespace


class Assignment(Statement):

    def __init__(self, name, expression):
        self.__name = name
        self.__expression = expression

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def expression(self) -> Expression:
        return self.__expression

    def evaluate(self, st) -> ASTNode:
        identifier = self.name.identifier
        namespaces = list([self.expression.evaluate(st)])
        st.insert(identifier, namespaces)
        return None


class Break(Statement):

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    def evaluate(self, st) -> ASTNode:
        return self


class Continue(Statement):
    
    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    def evaluate(self, st) -> ASTNode:
        return self


class Return(Statement):

    __value = None

    def __init__(self, expression):
        self.__expression = expression

    @property
    def expression(self) -> Expression:
        return self.__expression

    @property
    def value(self) -> typing.Any:
        return self.__value

    def evaluate(self, st) -> ASTNode:
        self.__value = self.expression.evaluate(st).value
        return self


class Elif(Statement):

    def __init__(self, expression, block, else_block=None):
        self.__expression = expression
        self.__block = block
        self.__else_block = else_block

    @property
    def expression(self) -> Expression:
        return self.__expression
    
    @property
    def block(self) -> Block:
        return self.__block

    @property
    def else_block(self) -> Block:
        return self.__else_block

    def evaluate(self, st) -> ASTNode:
        return self.block.evaluate(st)


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
    def expression(self) -> Expression:
        return self.__expression
    
    @property
    def block(self) -> Block:
        return self.__block

    @property
    def elif_statements(self) -> list[Elif]:
        return self.__elif_statements

    @property
    def else_block(self) -> Block:
        return self.__else_block

    def evaluate(self, st) -> ASTNode:
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


class Iterate(Statement):

    def __init__(self, iterable, variable, block):
        self.__iterable = iterable
        self.__variable = variable
        self.__block = block

    @property
    def iterable(self) -> Expression:
        return self.__iterable
    
    @property
    def variable(self) -> Name:
        return self.__variable

    @property
    def block(self) -> Block:
        return self.__block

    def evaluate(self, st) -> ASTNode:
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
    def expression(self) -> Expression:
        return self.__expression
    
    @property
    def block(self) -> Block:
        return self.__block

    def evaluate(self, st) -> ASTNode:
        while (self.expression.evaluate(st).value):
            node = self.block.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                break
            elif (isinstance(node, Continue)):
                continue
        return None


class Property(Statement):

    def __init__(self, name):
        self.__name = name

    @property
    def name(self) -> Name:
        return self.__name

    def evaluate(self, st) -> ASTNode:
        # TODO
        pass


class FunctionDef(Statement):

    __value = None

    def __init__(self, name, parameters, body, **flags):
        self.__name = name
        self.__parameters = parameters
        self.__body = body
        self.__flags = flags

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def parameters(self) -> list[Name]:
        return self.__parameters

    @property
    def body(self) -> Block:
        return self.__body

    @property
    def flags(self) -> dict[str, typing.Any]:
        return self.__flags

    @property
    def value(self):
        return self.__value

    def evaluate(self, st) -> ASTNode:
        self.__value = builtins.Function(self.name, self.parameters, self.body, **self.flags)
        identifier = self.name.identifier
        namespaces = list([self])
        st.insert(identifier, namespaces, isnamespace=True)
        return None


class ClassDef(Statement):

    __value = None

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
    def name(self) -> Name:
        return self.__name

    @property
    def superclasses(self) -> list[Name]:
        return self.__superclasses

    @property
    def block(self) -> Block:
        return self.__block

    @property
    def flags(self) -> dict[str, typing.Any]:
        return self.__flags

    @property
    def properties(self) -> list[Property]:
        return self.__properties

    @property
    def methods(self) -> list[FunctionDef]:
        return self.__methods

    @property
    def value(self):
        return self.__value

    def evaluate(self, st) -> ASTNode:
        self.__value = builtins.Class(self.name, self.superclasses, self.properties, self.methods, **self.flags)
        identifier = self.name.identifier
        namespaces = list([self])
        st.insert(identifier, namespaces, isnamespace=True)
        return None


class Or(Expression):

    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
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
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
        right = self.right.evaluate(st)
        value = +right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class UMinus(Expression):

    def __init__(self, right):
        self.__right = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st) -> ASTNode:
        right = self.right.evaluate(st)
        value = -right.value
        node = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Boolean(Expression):

    __value = None

    def __init__(self, literal):
        self.__literal = literal

    @property
    def literal(self):
        return self.__literal

    @property
    def value(self) -> builtins.Boolean:
        return self.__value

    def evaluate(self, st) -> ASTNode:
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
    def value(self) -> builtins.Null:
        return self.__value

    def evaluate(self, st) -> ASTNode:
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
    def value(self) -> builtins.String:
        return self.__value

    def evaluate(self, st) -> ASTNode:
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
    def value(self) -> builtins.Integer:
        return self.__value

    def evaluate(self, st) -> ASTNode:
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
    def value(self) -> builtins.Float:
        return self.__value

    def evaluate(self, st) -> ASTNode:
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
    def value(self) -> builtins.Complex:
        return self.__value

    def evaluate(self, st) -> ASTNode:
        self.__value = builtins.Complex(complex(self.literal))
        return self


class Tuple(Expression):

    __value = None
    __iterable = None

    def __init__(self, expressions):
        self.__expressions = expressions

    @property
    def expressions(self) -> list[Expression]:
        return self.__expressions

    @property
    def value(self) -> builtins.Tuple:
        return self.__value

    @property
    def iterable(self) -> tuple[Expression]:
        return self.__iterable
    
    def evaluate(self, st) -> ASTNode:
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
    def expressions(self) -> Expression:
        return self.__expressions

    @property
    def value(self) -> builtins.List:
        return self.__value

    @property
    def iterable(self) -> list[Expression]:
        return self.__iterable
    
    def evaluate(self, st) -> ASTNode:
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
    def kvpairs(self) -> list[tuple[Expression, Expression]]:
        return self.__kvpairs

    @property
    def value(self) -> builtins.Dict:
        return self.__value

    @property
    def iterable(self) -> dict[Expression, Expression]:
        return self.__iterable

    def evaluate(self, st) -> ASTNode:
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
    def name(self) -> Name:
        return self.__name

    @property
    def arguments(self) -> list[Expression]:
        return self.__arguments
    
    def evaluate(self, st) -> ASTNode:
        # Get function definition and its attributes
        identifier = self.name.identifier
        namespace = st.lookup(identifier).namespace

        if (isinstance(namespace, ClassDef)):
            classdef = namespace
            superclasses = classdef.superclasses
            properties = classdef.properties
            methods = classdef.methods
            instancest = symtable.Class(identifier, parent=st)

            # TODO: Insert symbols for properties
            # TODO: Insert methods for properties

            # Evaluate constructor
            constructor: FunctionDef = methods['init']
            constructor.evaluate(instancest)
            call = Call(Name('init'), self.arguments)
            call.evaluate(instancest)

            # Return class instance
            return builtins.Object(identifier, instancest)

        elif (isinstance(namespace, FunctionDef)):
            functiondef = namespace
            parameters = functiondef.parameters
            body = functiondef.body
            functionst = symtable.Function(identifier, parent=st)

            # Insert symbols for arguments
            for index in range(len(parameters)):
                parameter = parameters[index]
                identifier = parameter.identifier
                namespaces = list([self.arguments[index].evaluate(st)])
                functionst.insert(identifier, namespaces, isparameter=True)
            
            # Evaluate function body
            if (functiondef.flags.get('isbuiltin', False)):
                functionptr = functiondef.flags.get('ptr', None)
                args = dict()
                for parameter in parameters:
                    value = parameter.evaluate(functionst).value
                    args[parameter.identifier] = value
                value = functionptr(**args)
                return TYPE[type(value)](value)
            else:
                block = body
                node = block.evaluate(functionst)
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
