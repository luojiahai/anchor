import abc
import types
import typing
import anchor.builtins as builtins
import anchor.symtable as symtable
import anchor.factory as factory


__all__: list[str] = []


class ASTNode(abc.ABC):

    @abc.abstractmethod
    def evaluate(self, st): pass


class Iterable(abc.ABC):

    @abc.abstractmethod
    def index(self, key): pass


class Callable(abc.ABC):

    @abc.abstractmethod
    def call(self, arguments, st): pass


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
        astnode: ASTNode = symbol.astnode
        return astnode


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
        astnodes: list[ASTNode] = list([self.expression.evaluate(st)])
        st.insert(identifier, astnodes)
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

    __value: builtins.Type = None

    def __init__(self, expression: Expression):
        self.__expression: Expression = expression

    @property
    def expression(self) -> Expression:
        return self.__expression

    @property
    def value(self) -> builtins.Type:
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
            astnodes: list[ASTNode] = list([element])
            st.insert(identifier, astnodes)
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


class Annotation(Statement):

    __value: builtins.Annotation = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.Annotation:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Annotation(str(self.literal))
        return self


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
        astnode: ASTNode = symbol.astnode
        return astnode


class FunctionDef(Statement, Callable):

    __value: builtins.Function = None

    def __init__(
        self, name: Name, parameters: list[Parameter], block: Block, **kwargs
    ):
        self.__name: Name = name
        self.__parameters: list[Parameter] = parameters
        self.__block: Block = block
        self.__kwargs: dict[str, typing.Any] = kwargs

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
    def kwargs(self) -> dict[str, typing.Any]:
        return self.__kwargs

    @property
    def value(self) -> builtins.Function:
        return self.__value

    def call(
        self, arguments: list[Expression], parentst: symtable.SymbolTable
    ) -> ASTNode:
        parameters: list[Parameter] = self.parameters
        block: Block = self.block
        functionst: symtable.Function = factory.SYMTABLE.new(
            symtable.Type.FUNCTION, 
            identifier=self.name.identifier, parent=parentst,
        )

        # Insert symbols for arguments
        for index in range(len(parameters)):
            parameter: Parameter = parameters[index]
            identifier: str = parameter.name.identifier
            astnodes: list[ASTNode] = list([
                arguments[index].evaluate(parentst)
            ])
            functionst.insert(identifier, astnodes, isparameter=True)
        
        # Evaluate function block
        if (self.kwargs.get('isbuiltin', False)):
            functionpointer: types.FunctionType = self.kwargs.get(
                'pointer', None
            )
            args: dict = dict()
            for parameter in parameters:
                value: builtins.Type = parameter.evaluate(functionst).value
                args[parameter.name.identifier] = value
            returnvalue: typing.Any = functionpointer(**args)
            return factory.AST.new(literal=returnvalue)
        else:
            node: ASTNode = block.evaluate(functionst)
            return node

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Function()
        identifier: str = self.name.identifier
        astnodes: list[ASTNode] = list([self])
        st.insert(identifier, astnodes)
        return self


class Property(Statement):

    __value: builtins.Property = None

    def __init__(self, name: Name, annotations: list[Annotation]):
        self.__name: Name = name
        self.__annotations: list[Annotation] = annotations

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def annotations(self) -> list[Annotation]:
        return self.__annotations

    @property
    def value(self) -> builtins.Property:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Property()
        identifier: str = self.name.identifier
        astnodes: list[ASTNode] = list([self])
        st.insert(identifier, astnodes)
        return self


class MethodDef(Statement, Callable):

    __value: builtins.Method = None

    def __init__(
        self, name: Name, parameters: list[Parameter], block: Block,
        annotations: list[Annotation], **kwargs
    ):
        self.__name: Name = name
        self.__parameters: list[Parameter] = parameters
        self.__block: Block = block
        self.__annotations: list[Annotation] = annotations
        self.__kwargs: dict[str, typing.Any] = kwargs

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
    def annotations(self) -> list[Annotation]:
        return self.__annotations

    @property
    def kwargs(self) -> dict[str, typing.Any]:
        return self.__kwargs

    @property
    def value(self) -> builtins.Method:
        return self.__value

    def call(
        self, arguments: list[Expression], parentst: symtable.SymbolTable
    ) -> ASTNode:
        parameters: list[Parameter] = self.parameters
        block: Block = self.block
        methodst: symtable.Function = factory.SYMTABLE.new(
            symtable.Type.FUNCTION, 
            identifier=self.name.identifier, parent=parentst,
        )

        # Insert symbols for arguments
        for index in range(len(parameters)):
            parameter: Parameter = parameters[index]
            identifier: str = parameter.name.identifier
            astnodes: list[ASTNode] = list([
                arguments[index].evaluate(parentst)
            ])
            methodst.insert(identifier, astnodes, isparameter=True)
        
        # Evaluate method block
        node: ASTNode = block.evaluate(methodst)
        return node

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Method()
        identifier: str = self.name.identifier
        astnodes: list[ASTNode] = list([self])
        st.insert(identifier, astnodes)
        return self


class ClassDef(Statement, Callable):

    __value: builtins.Class = None

    def __init__(self, name: Name, block: Block, annotations: list[Annotation], **kwargs):
        self.__name: Name = name
        self.__block: Block = block
        self.__annotations: list[Annotation] = annotations
        self.__kwargs: dict[str, typing.Any] = kwargs

        self.__properties: dict[str, Property] = dict()
        self.__methods: dict[str, MethodDef] = dict()
        for statement in self.__block.statements:
            if (isinstance(statement, Property)):
                identifier = statement.name.identifier
                self.__properties[identifier] = statement
            elif (isinstance(statement, MethodDef)):
                identifier = statement.name.identifier
                self.__methods[identifier] = statement

        # default factory
        if (name.identifier not in self.__methods):
            parameters = list()
            block = Block(list())
            self.__methods[name.identifier] = \
                MethodDef(name, parameters, block, list())

    @property
    def name(self) -> Name:
        return self.__name

    @property
    def block(self) -> Block:
        return self.__block

    @property
    def kwargs(self) -> dict[str, typing.Any]:
        return self.__kwargs

    @property
    def properties(self) -> dict[str, Property]:
        return self.__properties

    @property
    def methods(self) -> dict[str, MethodDef]:
        return self.__methods

    @property
    def annotations(self) -> list[Annotation]:
        return self.__annotations

    @property
    def value(self) -> builtins.Class:
        return self.__value

    def call(
        self, arguments: list[Expression], parentst: symtable.SymbolTable
    ) -> ASTNode:
        properties: dict[str, Property] = self.properties
        methods: dict[str, MethodDef] = self.methods
        instancest: symtable.Class = factory.SYMTABLE.new(
            symtable.Type.CLASS, 
            identifier=self.name.identifier, parent=parentst,
        )

        # Insert symbols for properties
        for _, prop in properties.items():
            astnodes: list[ASTNode] = list([prop])
            instancest.insert(
                prop.name.identifier, astnodes, isproperty=True
            )

        # Insert symbols for methods
        for _, method in methods.items():
            astnodes: list[ASTNode] = list([method])
            instancest.insert(
                method.name.identifier, astnodes, ismethod=True
            )

        # Evaluate constructor
        factorymethod: MethodDef = methods[self.name.identifier]
        factorymethod.evaluate(instancest)
        call: Call = Call(Name(self.name.identifier), arguments)
        call.evaluate(instancest)

        # Return class instance
        return Instance(self, instancest)

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Class()
        identifier: str = self.name.identifier
        astnodes: list[ASTNode] = list([self])
        st.insert(identifier, astnodes)
        return self


class Instance(Statement):

    __value: builtins.Instance = None

    def __init__(self, classdef: ClassDef, instancest: symtable.Class):
        self.__classdef: ClassDef = classdef
        self.__instancest = instancest

    @property
    def classdef(self) -> ClassDef:
        return self.__classdef

    @property
    def instancest(self) -> symtable.Class:
        return self.__instancest

    @property
    def value(self) -> builtins.Instance:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Instance(self.classdef.value)
        return self


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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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
        node: Expression = factory.AST.new(literal=value)
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


class String(Expression, Iterable):

    __value: builtins.String = None

    def __init__(self, literal: typing.Any):
        self.__literal: typing.Any = literal

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def value(self) -> builtins.String:
        return self.__value

    def index(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(literal=item)

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


class Tuple(Expression, Iterable):

    __literal: typing.Any = None
    __value: builtins.Tuple = None
    __iterable: tuple = None

    def __init__(self, **kwargs):
        literal: typing.Any = kwargs.get('literal', None)
        if (literal):
            self.__literal = literal
        else:
            expressions = kwargs.get('expressions', None)
            self.__expressions: list[Expression] = expressions

    @property
    def literal(self):
        return self.__literal

    @property
    def expressions(self) -> list[Expression]:
        return self.__expressions

    @property
    def value(self) -> builtins.Tuple:
        return self.__value

    @property
    def iterable(self) -> tuple[Expression]:
        return self.__iterable

    def index(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(literal=item)
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.literal):
            self.__value = builtins.Tuple(tuple(self.literal))
        else:
            self.__value = builtins.Tuple(tuple([
                expression.evaluate(st).value
                for expression in self.expressions
            ]))
            self.__iterable = tuple([
                expression.evaluate(st)
                for expression in self.expressions
            ])
        return self


class List(Expression, Iterable):

    __literal: typing.Any = None
    __value: builtins.List = None
    __iterable: list[Expression] = None

    def __init__(self, **kwargs):
        literal: typing.Any = kwargs.get('literal', None)
        if (literal):
            self.__literal = literal
        else:
            expressions = kwargs.get('expressions', None)
            self.__expressions: list[Expression] = expressions

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def expressions(self) -> Expression:
        return self.__expressions

    @property
    def value(self) -> builtins.List:
        return self.__value

    @property
    def iterable(self) -> list[Expression]:
        return self.__iterable

    def index(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(literal=item)
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.literal):
            self.__value = builtins.List(list(self.literal))
        else:
            self.__value = builtins.List(list([
                expression.evaluate(st).value
                for expression in self.expressions
            ]))
            self.__iterable = list([
                expression.evaluate(st) 
                for expression in self.expressions
            ])
        return self


class Dict(Expression, Iterable):

    __literal: typing.Any = None
    __value: builtins.Dict = None
    __iterable: dict[Expression, Expression] = None

    def __init__(self, **kwargs):
        literal: typing.Any = kwargs.get('literal', None)
        if (literal):
            self.__literal = literal
        else:
            kvpairs = kwargs.get('kvpairs', None)
            self.__kvpairs: list[tuple[Expression, Expression]] = kvpairs

    @property
    def literal(self) -> typing.Any:
        return self.__literal

    @property
    def kvpairs(self) -> list[tuple[Expression, Expression]]:
        return self.__kvpairs

    @property
    def value(self) -> builtins.Dict:
        return self.__value

    @property
    def iterable(self) -> dict[Expression, Expression]:
        return self.__iterable

    def index(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(literal=item)

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.literal):
            self.__value = builtins.Dict(dict(self.literal))
        else:
            self.__value = builtins.Dict({
                k.evaluate(st).value: v.evaluate(st).value
                for k, v in self.kvpairs
            })
            self.__iterable = dict({
                k.evaluate(st): v.evaluate(st)
                for k, v in self.kvpairs
            })
        return self


class DotName(Expression):

    def __init__(self, expression: Expression, name: Name):
        self.__expression: Expression = expression
        self.__name: Name = name

    @property
    def expression(self) -> Expression:
        return self.__expression

    @property
    def name(self) -> Name:
        return self.__name

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        return self


class Call(Expression):

    def __init__(self, expression: Expression, arguments: list[Expression]):
        self.__expression: Expression = expression
        self.__arguments: list[Expression] = arguments

    @property
    def expression(self) -> Expression:
        return self.__expression

    @property
    def arguments(self) -> list[Expression]:
        return self.__arguments
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        name: Name = None
        if (isinstance(self.expression, Name)):
            name = self.expression
        elif (isinstance(self.expression, DotName)):
            dotname: DotName = self.expression
            instancename: Name = dotname.expression
            instance: Instance = st.lookup(instancename.identifier).astnode
            st = instance.instancest
            name = dotname.name
        else:
            # TODO: recursively resolve preceding expression
            node: ASTNode = self.expression.evaluate(st)
        
        # Get node and call
        identifier: str = name.identifier
        astnode: ASTNode = st.lookup(identifier).astnode
        if (isinstance(astnode, Callable)):
            return astnode.call(self.arguments, st)


factory.AST = factory.ASTNodeFactory(declarations=list([
    ('Boolean', Boolean,),
    ('Null', Null,),
    ('Integer', Integer,),
    ('Float', Float,),
    ('Complex', Complex,),
    ('String', String,),
    ('Tuple', Tuple,),
    ('List', List,),
    ('Dict', Dict,),
]))
