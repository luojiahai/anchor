import abc
import typing
import anchor.builtins as builtins
import anchor.symtable as symtable
import anchor.factory as factory


class ASTNode(abc.ABC):

    @abc.abstractmethod
    def evaluate(self, st: symtable.SymbolTable): pass


class Expression(ASTNode): pass


class Statement(ASTNode): pass


class Block(ASTNode):

    def __init__(self, statements: list[Statement]):
        self.__statements: list[Statement] = statements

    @property
    def statements(self) -> list[Statement]:
        return self.__statements

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        for statement in self.statements:
            node: ASTNode = statement.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                return node
            elif (isinstance(node, Continue)):
                return node
        return None


class Program(ASTNode):

    def __init__(self, block: Block):
        self.__block: Block = block

    @property
    def block(self) -> Block:
        return self.__block
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        node: ASTNode = self.block.evaluate(st)
        return node


class Name(Expression):

    def __init__(self, identifier: str):
        self.__identifier: str = identifier

    @property
    def identifier(self) -> str:
        return self.__identifier

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        symbol: symtable.Symbol = st.lookup(self.identifier)
        namespace: ASTNode = symbol.namespace
        return namespace


class Assignment(Statement):

    def __init__(self, name: Name, expression: Expression):
        self.__name: Name = name
        self.__expression: Expression = expression

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def expression(self) -> Expression:
        return self.__expression

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        identifier: str = self.name.identifier
        namespaces: list[ASTNode] = list([self.expression.evaluate(st)])
        st.insert(identifier, namespaces)
        return None


class Break(Statement):

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        return self


class Continue(Statement):
    
    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        return self


class Return(Statement):

    __value: typing.Any = None

    def __init__(self, expression: Expression):
        self.__expression: Expression = expression

    @property
    def expression(self) -> Expression:
        return self.__expression

    @property
    def value(self) -> typing.Any:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = self.expression.evaluate(st).value
        return self


class Elif(Statement):

    def __init__(self, 
        expression: Expression, block: Block, elseblock: Block = None
    ):
        self.__expression: Expression = expression
        self.__block: Block = block
        self.__elseblock: Block = elseblock

    @property
    def expression(self) -> Expression:
        return self.__expression
    
    @property
    def block(self) -> Block:
        return self.__block

    @property
    def elseblock(self) -> Block:
        return self.__elseblock

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        return self.block.evaluate(st)


class If(Statement):

    def __init__(
        self, expression: Expression, block: Block, 
        elifs: list[Elif] = list(), elseblock: Block = None
    ):
        self.__expression: Expression = expression
        self.__block: Block = block
        self.__elifs: list[Elif] = elifs
        self.__elseblock: Block = elseblock

    @property
    def expression(self) -> Expression:
        return self.__expression
    
    @property
    def block(self) -> Block:
        return self.__block

    @property
    def elifs(self) -> list[Elif]:
        return self.__elifs

    @property
    def elseblock(self) -> Block:
        return self.__elseblock

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.expression.evaluate(st).value):
            return self.block.evaluate(st)
        else:
            for elif_ in self.elifs:
                if (elif_.expression.evaluate(st).value):
                    return elif_.evaluate(st)
                elif (elif_.elseblock):
                    return elif_.elseblock.evaluate(st)
            
            if (self.elseblock):
                return self.elseblock.evaluate(st)
            return None


class Iterate(Statement):

    def __init__(self, iterable: Expression, variable: Name, block: Block):
        self.__iterable: Expression = iterable
        self.__variable: Name = variable
        self.__block: Block = block

    @property
    def iterable(self) -> Expression:
        return self.__iterable
    
    @property
    def variable(self) -> Name:
        return self.__variable

    @property
    def block(self) -> Block:
        return self.__block

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        identifier: str = self.variable.identifier
        for element in self.iterable.evaluate(st).iterable:
            namespaces: list[ASTNode] = list([element])
            st.insert(identifier, namespaces)
            node: ASTNode = self.block.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                break
            elif (isinstance(node, Continue)):
                continue
        return None


class Loop(Statement):

    def __init__(self, expression: Expression, block: Block):
        self.__expression: Expression = expression
        self.__block: Block = block

    @property
    def expression(self) -> Expression:
        return self.__expression
    
    @property
    def block(self) -> Block:
        return self.__block

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        while (self.expression.evaluate(st).value):
            node: ASTNode = self.block.evaluate(st)
            if (isinstance(node, Return)):
                return node
            elif (isinstance(node, Break)):
                break
            elif (isinstance(node, Continue)):
                continue
        return None


class Property(Statement):

    def __init__(self, name: Name):
        self.__name: Name = name

    @property
    def name(self) -> Name:
        return self.__name

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        # TODO
        pass


class Parameter(Statement):

    def __init__(self, name: Name, typename: Name = None):
        self.__name: Name = name
        self.__typename: Name = typename

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def typename(self) -> Name:
        return self.__typename

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        symbol: symtable.Symbol = st.lookup(self.name.identifier)
        namespace: ASTNode = symbol.namespace
        return namespace


class FunctionDef(Statement):

    __value: builtins.Function = None

    def __init__(
        self, name: Name, parameters: list[Parameter], block: Block, **flags
    ):
        self.__name: Name = name
        self.__parameters: list[Parameter] = parameters
        self.__block: Block = block
        self.__flags: dict[str, typing.Any] = flags

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def parameters(self) -> list[Parameter]:
        return self.__parameters

    @property
    def block(self) -> Block:
        return self.__block

    @property
    def flags(self) -> dict[str, typing.Any]:
        return self.__flags

    @property
    def value(self) -> builtins.Function:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Function()
        identifier: str = self.name.identifier
        namespaces: list[ASTNode] = list([self])
        st.insert(identifier, namespaces, isnamespace=True)
        return None


class ClassDef(Statement):

    __value: builtins.Class = None

    def __init__(
        self, name: Name, superclasses: list[Name], block: Block, **flags
    ):
        self.__name: Name = name
        self.__superclasses: list[Name] = superclasses
        self.__block: Block = block
        self.__flags: dict[str, typing.Any] = flags

        self.__properties: dict = dict()
        self.__methods: dict = dict()
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
            block = Block(list())
            self.__methods['init'] = FunctionDef(name, parameters, block)

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
    def properties(self) -> dict[str, Property]:
        return self.__properties

    @property
    def methods(self) -> dict[str, FunctionDef]:
        return self.__methods

    @property
    def value(self) -> builtins.Class:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Class()
        identifier: str = self.name.identifier
        namespaces: list[ASTNode] = list([self])
        st.insert(identifier, namespaces, isnamespace=True)
        return None


class Or(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value or right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class And(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value and right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Not(Expression):

    def __init__(self, right: Expression):
        self.__right: Expression = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        right: Expression = self.right.evaluate(st)
        value: typing.Any = not right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class EqEqual(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value == right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class NotEqual(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value != right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Less(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value < right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class LessEqual(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value <= right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Greater(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value > right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class GreaterEqual(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value >= right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Plus(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value + right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Minus(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value - right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Star(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value * right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class DoubleStar(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value ** right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Slash(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value / right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class DoubleSlash(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value // right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Percent(Expression):

    def __init__(self, left: Expression, right: Expression):
        self.__left: Expression = left
        self.__right: Expression = right

    @property
    def left(self) -> Expression:
        return self.__left

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        left: Expression = self.left.evaluate(st)
        right: Expression = self.right.evaluate(st)
        value: typing.Any = left.value % right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class UPlus(Expression):

    def __init__(self, right: Expression):
        self.__right: Expression = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        right: Expression = self.right.evaluate(st)
        value: typing.Any = +right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class UMinus(Expression):

    def __init__(self, right: Expression):
        self.__right: Expression = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        right: Expression = self.right.evaluate(st)
        value: typing.Any = -right.value
        node: Expression = TYPE[type(value)](value)
        node.evaluate(st)
        return node


class Boolean(Expression):

    __value: builtins.Boolean = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.Boolean:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Boolean(bool(self.literal))
        return self


class Null(Expression):

    __value: builtins.Null = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.Null:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Null(self.literal)
        return self


class String(Expression):

    __value: builtins.String = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.String:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.String(str(self.literal))
        return self


class Integer(Expression):

    __value: builtins.Integer = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.Integer:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Integer(int(self.literal))
        return self


class Float(Expression):

    __value: builtins.Float = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.Float:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Float(float(self.literal))
        return self


class Complex(Expression):

    __value: builtins.Complex = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.Complex:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Complex(complex(self.literal))
        return self


class Tuple(Expression):

    __value: builtins.Tuple = None
    __iterable: tuple[Expression] = None

    def __init__(self, expressions: list[Expression]):
        self.__expressions: list[Expression] = expressions

    @property
    def expressions(self) -> list[Expression]:
        return self.__expressions

    @property
    def value(self) -> builtins.Tuple:
        return self.__value

    @property
    def iterable(self) -> tuple[Expression]:
        return self.__iterable
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
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

    __value: builtins.List = None
    __iterable: list[Expression] = None

    def __init__(self, expressions: list[Expression]):
        self.__expressions: list[Expression] = expressions

    @property
    def expressions(self) -> Expression:
        return self.__expressions

    @property
    def value(self) -> builtins.List:
        return self.__value

    @property
    def iterable(self) -> list[Expression]:
        return self.__iterable
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
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

    __value: builtins.Dict = None
    __iterable: dict[Expression, Expression] = None

    def __init__(self, kvpairs: list[tuple[Expression, Expression]]):
        self.__kvpairs: list[tuple[Expression, Expression]] = kvpairs

    @property
    def kvpairs(self) -> list[tuple[Expression, Expression]]:
        return self.__kvpairs

    @property
    def value(self) -> builtins.Dict:
        return self.__value

    @property
    def iterable(self) -> dict[Expression, Expression]:
        return self.__iterable

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
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

    def __init__(self, name: Name, arguments: list[Expression]):
        self.__name: Name = name
        self.__arguments: list[Expression] = arguments

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def arguments(self) -> list[Expression]:
        return self.__arguments
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        # Get function definition and its attributes
        identifier: str = self.name.identifier
        namespace: ASTNode = st.lookup(identifier).namespace

        if (isinstance(namespace, ClassDef)):
            classdef: ClassDef = namespace
            superclasses: list = classdef.superclasses
            properties: dict[str, Property] = classdef.properties
            methods: dict[str, FunctionDef] = classdef.methods
            instancest: symtable.Class = factory.SymbolTableFactory().new(
                'Class', identifier=identifier, parent=st
            )

            # TODO: Insert symbols for properties
            # TODO: Insert methods for properties

            # Evaluate constructor
            constructor: FunctionDef = methods['init']
            constructor.evaluate(instancest)
            call: Call = Call(Name('init'), self.arguments)
            call.evaluate(instancest)

            # Return class instance
            return builtins.Object(identifier, instancest)

        elif (isinstance(namespace, FunctionDef)):
            functiondef: FunctionDef = namespace
            parameters: list[Parameter] = functiondef.parameters
            block: Block = functiondef.block
            functionst: symtable.Function = factory.SymbolTableFactory().new(
                'Function', identifier=identifier, parent=st
            )

            # Insert symbols for arguments
            for index in range(len(parameters)):
                parameter: Parameter = parameters[index]
                identifier: str = parameter.name.identifier
                namespaces: list[ASTNode] = list([
                    self.arguments[index].evaluate(st)
                ])
                functionst.insert(identifier, namespaces, isparameter=True)
            
            # Evaluate function block
            if (functiondef.flags.get('isbuiltin', False)):
                functionpointer: function = functiondef.flags.get(
                    'pointer', None
                )
                args: dict = dict()
                for parameter in parameters:
                    value: typing.Any = parameter.evaluate(functionst).value
                    args[parameter.name.identifier] = value
                value: typing.Any = functionpointer(**args)
                return TYPE[type(value)](value)
            else:
                node: ASTNode = block.evaluate(functionst)
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
