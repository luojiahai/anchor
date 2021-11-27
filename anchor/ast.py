from abc import *
from anchor.symtable import *


class ASTNode(ABC):

    @abstractmethod
    def evaluate(self, symtable): pass

