from abc import *


class AnchorType(ABC):
    
    def __init__(self, type_name):
        self._type = type_name

    @property
    def type(self):
        return self._type


class Null(AnchorType):

    def __init__(self, value):
        super().__init__('NullType')


class Boolean(AnchorType, int):

    def __init__(self, value):
        super().__init__('Boolean')


class Integer(AnchorType, int):
    
    def __init__(self, value):
        super().__init__('Integer')


class Float(AnchorType, float):

    def __init__(self, value):
        super().__init__('Float')


class Complex(AnchorType, complex):
    
    def __init__(self, value):
        super().__init__('Complex')


class String(AnchorType, str):
    
    def __init__(self, value):
        super().__init__('String')


class Tuple(AnchorType, tuple): 
    
    def __init__(self, value):
        super().__init__('Tuple')

    def __new__(self, value):
        return tuple.__new__(self, value)


class List(AnchorType, list):

    def __init__(self, value):
        super().__init__('List')
        self.extend(value)


class Dict(AnchorType, dict):

    def __init__(self, value):
        super().__init__('List')
        self.update(value)

