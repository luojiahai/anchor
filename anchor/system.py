import sys
import typing
import logging


__all__: list[str] = ['GLOBAL',]


class Global(object):

    class __Global(object):

        def __init__(self):
            self.__debug: bool = False
            self.__debuglex: bool = False
            self.__debugyacc: bool = False
            self.__inputstream: typing.TextIO = sys.stdin
            self.__outputstream: typing.TextIO = sys.stdout
            self.__errorstream: typing.TextIO = sys.stderr
            self.__logstream: typing.TextIO = sys.stderr
            self.__log: logging.Logger = None

        @property
        def debug(self) -> bool:
            return self.__debug

        @debug.setter
        def debug(self, other: bool):
            self.__debug = other

        @property
        def debuglex(self) -> bool:
            return self.__debuglex

        @debuglex.setter
        def debuglex(self, other: bool):
            self.__debuglex = other

        @property
        def debugyacc(self) -> bool:
            return self.__debugyacc

        @debugyacc.setter
        def debugyacc(self, other: bool):
            self.__debugyacc = other

        @property
        def inputstream(self) -> typing.TextIO:
            return self.__inputstream

        @inputstream.setter
        def inputstream(self, other: typing.TextIO):
            self.__inputstream = other
            
        @property
        def outputstream(self) -> typing.TextIO:
            return self.__outputstream

        @outputstream.setter
        def outputstream(self, other: typing.TextIO):
            self.__outputstream = other

        @property
        def errorstream(self) -> typing.TextIO:
            return self.__errorstream

        @errorstream.setter
        def errorstream(self, other: typing.TextIO):
            self.__errorstream = other

        @property
        def logstream(self) -> typing.TextIO:
            return self.__logstream

        @logstream.setter
        def logstream(self, other: typing.TextIO):
            self.__logstream = other

        @property
        def log(self) -> logging.Logger:
            return self.__log

        @log.setter
        def log(self, other: logging.Logger):
            self.__log = other

    __instance: __Global = None

    def __new__(cls) -> __Global:
        if (not Global.__instance):
            Global.__instance = Global.__Global()
        return Global.__instance

GLOBAL: Global = Global()
