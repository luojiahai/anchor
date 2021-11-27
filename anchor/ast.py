import abc


class ASTNode(abc.ABC):

    @abc.abstractmethod
    def evaluate(self, symtable): pass


class Program(ASTNode):

    def __init__(self, block):
        self.__block = block

    @property
    def block(self):
        return self.__block
    
    def evaluate(self, symtable):
        return self.block.evaluate(symtable)


class Block(ASTNode):

    def __init__(self, statements):
        self.__statements = statements

    @property
    def statements(self):
        return self.__statements

    def evaluate(self, symtable):
        for statement in self.statements:
            value = statement.evaluate(symtable)
            if (isinstance(value, Terminal)):
                return value
        return None


class Statement(ASTNode): pass


class Terminal(ASTNode): pass


class Assignment(Statement):

    def __init__(self, name, expression):
        self.__name = name
        self.__expression = expression

    def evaluate(self, symtable):
        identifier = self.__name.identifier
        flags = dict()
        namespaces = [self.__expression.evaluate(symtable)]
        symtable.insert(identifier, flags, namespaces)
        return None


class If(Statement):

    def __init__(self, expression, block, elif_statements=[], else_block=None):
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

    def evaluate(self, symtable):
        if (self.expression.evaluate(symtable)):
            return self.block.evaluate(symtable)
        else:
            for elif_statement in self.elif_statements:
                if (elif_statement.expression.evaluate(symtable)):
                    return elif_statement.evaluate(symtable)
                elif (elif_statement.else_block):
                    return elif_statement.else_block.evaluate(symtable)
            
            if (self.else_block):
                return self.else_block.evaluate(symtable)
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

    def evaluate(self, symtable):
        return self.block.evaluate(symtable)
