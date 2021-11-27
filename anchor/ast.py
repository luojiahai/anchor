import abc


class ASTNode(abc.ABC):

    @abc.abstractmethod
    def evaluate(self, symtable): pass

