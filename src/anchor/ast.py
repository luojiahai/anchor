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


class Atom(abc.ABC):

    __value: builtins.Type = None

    @property
    def value(self):
        return self.__value


class Iterable(abc.ABC):

    @abc.abstractmethod
    def __iter__(self): pass

    @abc.abstractmethod
    def __next__(self): pass

    @abc.abstractmethod
    def __getitem__(self, key): pass


class Callable(abc.ABC):

    @abc.abstractmethod
    def call(self, arguments, st): pass


class Expression(ASTNode):

    @abc.abstractmethod
    def evaluate(self, st) -> ASTNode: pass


class Statement(ASTNode):

    @abc.abstractmethod
    def evaluate(self, st) -> ASTNode: pass


class Block(ASTNode):

    def __init__(self, statements: list[Statement]):
        self.__statements: list[Statement] = statements

    @property
    def statements(self) -> list[Statement]:
        return self.__statements

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        for statement in self.statements:
            astnode: ASTNode = statement.evaluate(st)
            if (isinstance(astnode, Return)):
                return astnode
            elif (isinstance(astnode, Break)):
                return astnode
            elif (isinstance(astnode, Continue)):
                return astnode
        return None


class Program(ASTNode):

    def __init__(self, block: Block):
        self.__block: Block = block

    @property
    def block(self) -> Block:
        return self.__block
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        astnode: ASTNode = self.block.evaluate(st)
        return astnode


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
        astnode = self.expression.evaluate(st)
        astnodes: list[ASTNode] = list([astnode])
        st.insert(identifier, astnodes)
        return None


class Break(Statement):

    def __init__(self, literal: str):
        self.__literal: str = literal

    @property
    def literal(self) -> str:
        return self.__literal

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Continue(Statement):
    
    def __init__(self, literal: str):
        self.__literal: str = literal

    @property
    def literal(self) -> str:
        return self.__literal

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Return(Statement, Atom):

    __expression: Expression = None
    __value: builtins.Type = None

    def __init__(self, expression: Expression = None, value: builtins.Type = None):
        self.__expression = expression
        self.__value = value

    @property
    def expression(self) -> Expression:
        return self.__expression

    @property
    def value(self) -> builtins.Type:
        return self.__value

    def copy(self) -> ASTNode:
        return Return(value=self.value)

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.expression != None):
            atom: Atom = self.expression.evaluate(st)
            self.__value = atom.value
        return self.copy()


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
        astnode: ASTNode = self.block.evaluate(st)
        return astnode


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
        ifcondition: Atom = self.expression.evaluate(st)
        if (ifcondition.value):
            astnode: ASTNode = self.block.evaluate(st)
            return astnode
        else:
            for elifstatement in self.elifs:
                elifcondition: Atom = elifstatement.expression.evaluate(st)
                if (elifcondition.value):
                    astnode: ASTNode = elifstatement.evaluate(st)
                    return astnode
                elif (elifstatement.elseblock):
                    astnode: ASTNode = elifstatement.elseblock.evaluate(st)
                    return astnode
            
            if (self.elseblock):
                astnode: ASTNode = self.elseblock.evaluate(st)
                return astnode
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
        for item in self.iterable.evaluate(st):
            itemnode: ASTNode = item
            astnode: ASTNode = itemnode.evaluate(st)
            astnodes: list[ASTNode] = list([astnode])
            st.insert(identifier, astnodes)
            astnode: ASTNode = self.block.evaluate(st)
            if (isinstance(astnode, Return)):
                return astnode
            elif (isinstance(astnode, Break)):
                break
            elif (isinstance(astnode, Continue)):
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
        condition: Atom = self.expression.evaluate(st)
        while (condition.value):
            astnode: ASTNode = self.block.evaluate(st)
            condition = self.expression.evaluate(st)
            if (isinstance(astnode, Return)):
                return astnode
            elif (isinstance(astnode, Break)):
                break
            elif (isinstance(astnode, Continue)):
                continue
        return None


class Annotation(Statement, Atom):

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
        st
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


class FunctionDef(Statement, Atom, Callable):

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
            argument: Expression = arguments[index]
            astnode: ASTNode = argument.evaluate(parentst)
            astnodes: list[ASTNode] = list([astnode])
            functionst.insert(identifier, astnodes, isparameter=True)
        
        # Evaluate function block
        isbuiltin = self.kwargs.get('isbuiltin', False)
        if (isbuiltin):
            functionpointer: types.FunctionType = self.kwargs.get('pointer')
            args: dict[str, builtins.Type] = dict()
            for parameter in parameters:
                value: builtins.Type = parameter.evaluate(functionst).value
                args[parameter.name.identifier] = value
            returnvalue: typing.Any = functionpointer(**args)
            return factory.AST.new(value=returnvalue)
        else:
            astnode: ASTNode = block.evaluate(functionst)
            return astnode

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Function()
        identifier: str = self.name.identifier
        astnodes: list[ASTNode] = list([self])
        st.insert(identifier, astnodes)
        return self


class Property(Statement, Atom):

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


class MethodDef(Statement, Atom, Callable):

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
        astnode: ASTNode = block.evaluate(methodst)
        return astnode

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        self.__value = builtins.Method()
        identifier: str = self.name.identifier
        astnodes: list[ASTNode] = list([self])
        st.insert(identifier, astnodes)
        return self


class ClassDef(Statement, Atom, Callable):

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


class Instance(Statement, Atom):

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
        st
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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value or right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value and right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


class Not(Expression):

    def __init__(self, right: Expression):
        self.__right: Expression = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        right: Atom = self.right.evaluate(st)
        value: typing.Any = not right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value == right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value != right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value < right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value <= right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value > right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value >= right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value + right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value - right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value * right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value ** right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value / right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value // right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


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
        left: Atom = self.left.evaluate(st)
        right: Atom = self.right.evaluate(st)
        value: typing.Any = left.value % right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


class UPlus(Expression):

    def __init__(self, right: Expression):
        self.__right: Expression = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        right: Atom = self.right.evaluate(st)
        value: typing.Any = +right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


class UMinus(Expression):

    def __init__(self, right: Expression):
        self.__right: Expression = right

    @property
    def right(self) -> Expression:
        return self.__right

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        right: Atom = self.right.evaluate(st)
        value: typing.Any = -right.value
        astnode: Expression = factory.AST.new(value=value)
        return astnode


class Boolean(Expression, Atom):

    def __init__(self, value: bool):
        self.__literal: str = str(value)
        self.__value: builtins.Boolean = builtins.Boolean(bool(value))

    @property
    def literal(self) -> str:
        return self.__literal

    @property
    def value(self) -> builtins.Boolean:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Null(Expression, Atom):

    __literal: str = None
    __value: builtins.Null = None

    def __init__(self, literal: str = None, value: str = None):
        if (literal != None):
            self.__literal = literal
            self.__value = builtins.Null(str(self.literal))
        elif (value != None):
            self.__literal = str(value)
            self.__value = builtins.Null(str(value))

    @property
    def literal(self) -> str:
        return self.__literal

    @property
    def value(self) -> builtins.Null:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class String(Expression, Atom, Iterable):

    __literal: str = None
    __value: builtins.String = None

    def __init__(self, literal: str = None, value: str = None):
        if (literal != None):
            self.__literal = literal
            self.__value = builtins.String(str(self.literal))
        elif (value != None):
            self.__literal = str(value)
            self.__value = builtins.String(str(value))

    @property
    def literal(self) -> str:
        return self.__literal

    @property
    def value(self) -> builtins.String:
        return self.__value

    def __iter__(self):
        self.iter = self.value.__iter__()
        return self

    def __next__(self):
        item = self.iter.__next__()
        return factory.AST.new(value=item)

    def __getitem__(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(value=item)

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Integer(Expression, Atom):

    __literal: str = None
    __value: builtins.Integer = None

    def __init__(self, literal: str = None, value: int = None):
        if (literal != None):
            self.__literal = literal
            self.__value = builtins.Integer(int(self.literal))
        elif (value != None):
            self.__literal = str(value)
            self.__value = builtins.Integer(int(value))

    @property
    def literal(self) -> str:
        return self.__literal

    @property
    def value(self) -> builtins.Integer:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Float(Expression, Atom):

    __literal: str = None
    __value: builtins.Float = None

    def __init__(self, literal: str = None, value: float = None):
        if (literal != None):
            self.__literal = literal
            self.__value = builtins.Float(float(self.literal))
        elif (value != None):
            self.__literal = str(value)
            self.__value = builtins.Float(float(value))

    @property
    def literal(self) -> str:
        return self.__literal

    @property
    def value(self) -> builtins.Float:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Complex(Expression, Atom):

    __literal: str = None
    __value: builtins.Complex = None

    def __init__(self, literal: str = None, value: complex = None):
        if (literal != None):
            self.__literal = literal
            self.__value = builtins.Complex(complex(self.literal))
        elif (value != None):
            self.__literal = str(value)
            self.__value = builtins.Complex(complex(value))

    @property
    def literal(self) -> str:
        return self.__literal

    @property
    def value(self) -> builtins.Complex:
        return self.__value

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        st
        return self


class Tuple(Expression, Atom, Iterable):

    __expressions: list[Expression] = None
    __value: builtins.Tuple = None

    def __init__(
        self, expressions: list[Expression] = None,
        value: tuple = None 
        
    ):
        if (expressions != None):
            self.__expressions: list[Expression] = expressions
        elif (value != None):
            self.__value = builtins.Tuple(tuple(value))

    @property
    def expressions(self) -> list[Expression]:
        return self.__expressions

    @property
    def value(self) -> builtins.Tuple:
        return self.__value

    def __iter__(self):
        self.iter = self.value.__iter__()
        return self

    def __next__(self):
        item = self.iter.__next__()
        return factory.AST.new(value=item)

    def __getitem__(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(value=item)
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.expressions != None):
            atoms: list[Atom] = list([
                expression.evaluate(st)
                for expression in self.expressions
            ])
            self.__value = builtins.Tuple(tuple(map(
                lambda x: x.value, atoms,
            )))
        elif (self.value != None):
            pass
        return self


class List(Expression, Atom, Iterable):
    
    __expressions: list[Expression] = None
    __value: builtins.List = None

    def __init__(
        self, expressions: list[Expression] = None,
        value: list = None
    ):
        if (expressions != None):
            self.__expressions: list[Expression] = expressions
        elif (value != None):
            self.__value = builtins.List(list(value))

    @property
    def expressions(self) -> list[Expression]:
        return self.__expressions

    @property
    def value(self) -> builtins.List:
        return self.__value

    def __iter__(self):
        self.iter = self.value.__iter__()
        return self

    def __next__(self):
        item = self.iter.__next__()
        return factory.AST.new(value=item)

    def __getitem__(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(value=item)
    
    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.expressions != None):
            atoms: list[Atom] = list([
                expression.evaluate(st)
                for expression in self.expressions
            ])
            self.__value = builtins.List(list(map(
                lambda x: x.value, atoms,
            )))
        elif (self.value != None):
            pass
        return self


class Dict(Expression, Atom, Iterable):

    __kvpairs: list[tuple[Expression, Expression]] = None
    __value: builtins.Dict = None

    def __init__(
        self, kvpairs: list[tuple[Expression, Expression]] = None,
        value: dict = None
    ):
        if (kvpairs != None):
            self.__kvpairs: list[tuple[Expression, Expression]] = kvpairs
        elif (value != None):
            self.__value = builtins.Dict(dict(value))

    @property
    def kvpairs(self) -> list[tuple[Expression, Expression]]:
        return self.__kvpairs

    @property
    def value(self) -> builtins.Dict:
        return self.__value

    def __iter__(self):
        self.iter = self.value.__iter__()
        return self

    def __next__(self):
        item = self.iter.__next__()
        return factory.AST.new(value=item)

    def __getitem__(self, key):
        item = self.value.__getitem__(key)
        return factory.AST.new(value=item)

    def evaluate(self, st: symtable.SymbolTable) -> ASTNode:
        if (self.kvpairs != None):
            atoms: dict[Atom, Atom] = dict({
                k.evaluate(st): v.evaluate(st)
                for k, v in self.kvpairs
            })
            self.__value = builtins.Dict(dict(map(
                lambda item: (item[0].value, item[1].value), atoms.items(),
            )))
        elif (self.value != None):
            pass
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
        st
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
        astnode: ASTNode = None
        if (isinstance(self.expression, Name)):
            name = self.expression
            identifier: str = name.identifier
            astnode = st.lookup(identifier).astnode
        elif (isinstance(self.expression, DotName)):
            dotname: DotName = self.expression
            instancename: Name = dotname.expression
            instance: Instance = st.lookup(instancename.identifier).astnode
            st = instance.instancest
            name = dotname.name
            identifier: str = name.identifier
            astnode = st.lookup(identifier).astnode
        else:
            astnode = self.expression.evaluate(st)

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
