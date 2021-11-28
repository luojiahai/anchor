import sys


__all__ = ['GLOBAL',]


class Global(object):

    class __Global(object):

        def __init__(self):
            self.__debug = False
            self.__debuglex = False
            self.__debugyacc = False
            self.__inputstream = sys.stdin
            self.__outputstream = sys.stdout
            self.__errorstream = sys.stderr
            self.__logstream = sys.stderr
            self.__log = None

        @property
        def debug(self):
            return self.__debug

        @debug.setter
        def debug(self, other):
            self.__debug = other

        @property
        def debuglex(self):
            return self.__debuglex

        @debuglex.setter
        def debuglex(self, other):
            self.__debuglex = other

        @property
        def debugyacc(self):
            return self.__debugyacc

        @debugyacc.setter
        def debugyacc(self, other):
            self.__debugyacc = other

        @property
        def inputstream(self):
            return self.__inputstream

        @inputstream.setter
        def inputstream(self, other):
            self.__inputstream = other
            
        @property
        def outputstream(self):
            return self.__outputstream

        @outputstream.setter
        def outputstream(self, other):
            self.__outputstream = other

        @property
        def errorstream(self):
            return self.__errorstream

        @errorstream.setter
        def errorstream(self, other):
            self.__errorstream = other

        @property
        def logstream(self):
            return self.__logstream

        @logstream.setter
        def logstream(self, other):
            self.__logstream = other

        @property
        def log(self):
            return self.__log

        @log.setter
        def log(self, other):
            self.__log = other

    __instance = None

    def __new__(cls):
        if (not Global.__instance):
            Global.__instance = Global.__Global()
        return Global.__instance

GLOBAL = Global()
