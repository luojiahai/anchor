import typing
import types
import anchor.token as token


__all__: typing.List[str] = ['kwlist', 'iskeyword',]


kwlist: typing.List[str] = list(token.kwdict.values())

iskeyword: types.FunctionType = frozenset(kwlist).__contains__
