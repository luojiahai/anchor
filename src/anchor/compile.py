import typing
import inspect
import anchor.system as system
import anchor.parse as parse
import anchor.ast as ast
import anchor.symtable as symtable
import anchor.builtins as builtins
import anchor.factory as factory


__all__: typing.List[str] = list(['execute',])


def execute(data: str) -> typing.Any:
    # Define main symbol table
    mainidentifier: typing.Literal = 'Main'
    symboltable: symtable.SymbolTable = factory.SYMTABLE.new(
        symtable.Type.MAIN, identifier=mainidentifier
    )

    # Include builtin functions
    for identifier, functionpointer in builtins.FUNCTION.items():
        name = ast.Name(identifier)
        parameters: typing.List[ast.Parameter] = list([
            ast.Parameter(ast.Name(argument))
            for argument in inspect.getfullargspec(functionpointer)[0]
        ])
        functiondef: ast.FunctionDef = ast.FunctionDef(
            name, parameters, None, pointer=functionpointer, isbuiltin=True
        )
        functiondef.evaluate(symboltable)
    
    # Parse and evaluate abstract syntax tree
    parser: parse.AnchorParser = parse.AnchorParser(
        debuglex=system.GLOBAL.debuglex, 
        debugyacc=system.GLOBAL.debugyacc,
        debuglog=system.GLOBAL.logger
    )
    abstractsyntaxtree: ast.ASTNode = parser.parse(data)
    return abstractsyntaxtree.evaluate(symboltable)
