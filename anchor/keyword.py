import anchor.token as token


__all__ = ['kwlist', 'iskeyword',]


kwlist: list[str] = list(token.kwdict.values())

iskeyword = frozenset(kwlist).__contains__
