import types
import anchor.token as token


__all__: list[str] = ['kwlist', 'iskeyword',]


kwlist: list[str] = list(token.kwdict.values())

iskeyword: types.FunctionType = frozenset(kwlist).__contains__
