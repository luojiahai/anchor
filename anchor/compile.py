import inspect
import typing
import anchor.system as system
import anchor.parse as parse
import anchor.ast as ast
import anchor.symtable as symtable
import anchor.builtins as builtins


__all__ = ['execute',]


def execute(data: str) -> typing.Any:
    # Define main symbol table
    symboltable = symtable.SymbolTable('main')

    # Include builtin functions
    for identifier, functionpointer in builtins.FUNCTION.items():
        name = ast.Name(identifier)
        parameters = list([
            ast.Name(argument) 
            for argument in inspect.getfullargspec(functionpointer)[0]
        ])
        functiondef = ast.FunctionDef(
            name, parameters, None, pointer=functionpointer, isbuiltin=True,
        )
        functiondef.evaluate(symboltable)
    
    # Parse and evaluate abstract syntax tree
    parser = parse.AnchorParser(
        debuglex=system.GLOBAL.debuglex, 
        debugyacc=system.GLOBAL.debugyacc,
        debuglog=system.GLOBAL.log,
    )
    abstractsyntaxtree = parser.parse(data)
    return abstractsyntaxtree.evaluate(symboltable)
