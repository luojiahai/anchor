import sys
import os
import typing
import time
import logging
import anchor.system as system
import anchor.compile as compile
import anchor.builtins as builtins


__all__: typing.List[str] = list(['main',])


def default(str) -> str:
    return str + ' [Default: %default]'

def readcommand(argv: typing.List[str]) -> typing.Dict[str, typing.Any]:
    from optparse import OptionParser
    usage_str = 'anchor [option] [file]'
    parser = OptionParser(usage_str)

    parser.add_option(
        '--debug', action='store_true', dest='debug',
        help=default('debug'), default=False
    )

    parser.add_option(
        '--debug-lex', action='store_true', dest='debuglex',
        help=default('debug lex'), default=False
    )

    parser.add_option(
        '--debug-yacc', action='store_true', dest='debugyacc',
        help=default('debug yacc'), default=False
    )
    
    parser.add_option(
        '--input-stream', dest='inputstream',
        help=default('input stream'), default='stdin'
    )

    parser.add_option(
        '--output-stream', dest='outputstream',
        help=default('output stream'), default='stdout'
    )

    parser.add_option(
        '--error-stream', dest='errorstream',
        help=default('error stream'), default='stderr'
    )

    parser.add_option(
        '--log-stream', dest='logstream',
        help=default('log stream'), 
        default='stderr'
    )

    parser.add_option(
        '--log-file', action='store_true', dest='logfile',
        help=default('generate log file'), default=False
    )

    options, other = parser.parse_args(argv[1:])
    if (len(other) == 0):
        parser.error('no input file')
    if (len(other) > 1):
        parser.error('Command line input not understood: ' + str(other[1:]))

    args = dict()
    args['file'] = other[0]

    # Debug and log stream
    if (options.debug or options.debuglex or options.debugyacc):
        # Debug flags
        system.GLOBAL.debug = options.debug
        if (options.debuglex or options.debugyacc):
            system.GLOBAL.debug = True
            system.GLOBAL.debuglex = options.debuglex
            system.GLOBAL.debugyacc = options.debugyacc

    # Log stream
    logstream = None
    if (options.logfile):
        localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        logstream_path = f'./log/anchor_{localtime}.log'
        os.makedirs(os.path.dirname(logstream_path), exist_ok=True)
        logstream = open(logstream_path, 'w')
    elif (options.logstream in builtins.STREAM):
        logstream = builtins.STREAM[options.logstream]
    else:
        logstream = open(options.logstream, 'w')
    system.GLOBAL.logstream = logstream

    # Set up a logging object
    logging.basicConfig(
        level = logging.DEBUG,
        stream = system.GLOBAL.logstream,
        format = '[DEBUG] %(filename)s:%(lineno)d:%(message)s'
    )
    logger = logging.getLogger()
    system.GLOBAL.logger = logger

    # Input stream
    inputstream = None
    if (options.inputstream in builtins.STREAM):
        inputstream = builtins.STREAM[options.inputstream]
    else:
        inputstream = open(options.inputstream, 'r')
    system.GLOBAL.inputstream = inputstream

    # Output stream
    outputstream = None
    if (options.outputstream in builtins.STREAM):
        outputstream = builtins.STREAM[options.outputstream]
    else:
        outputstream = open(options.outputstream, 'w')
    system.GLOBAL.outputstream = outputstream

    # Error stream
    errorstream = None
    if (options.errorstream in builtins.STREAM):
        errorstream = builtins.STREAM[options.errorstream]
    else:
        errorstream = open(options.errorstream, 'w')
    system.GLOBAL.errorstream = errorstream

    return args

def readfile(file) -> str:
    f = open(file, "r", encoding='utf-8')
    data = f.read()
    f.close()
    return data

def main() -> typing.Any:
    args = readcommand(sys.argv)
    data = readfile(**args)
    return compile.execute(data)

main()
