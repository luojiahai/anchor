import typing
import anchor.token as token


__all__: typing.List[str] = list(['kwlist', 'iskeyword',])


kwlist: typing.List[str] = list(token.kwdict.values())

iskeyword: typing.Callable = frozenset(kwlist).__contains__
