# In an AST replace LINQ operations with the proper
# AST entries.
import clientlib.query_ast as query_ast
from clientlib.ast_util import wrap_lambda
import ast


def parse_ast (ast_text):
    '''Parse a string as a LINQ ast
    
    NOTE: This must be called for every AST that the framework is converting from text.

    ast_text: String containing a lambda function

    returns:

    ast: The python AST representing the function, with Select, SelectMany, etc., properly converted
         to function call AST's.
    '''
    a = ast.parse(ast_text)
    return replace_LINQ_operators().visit(a)

class replace_LINQ_operators(ast.NodeTransformer):
    r'''
    We are called on expressions that are parsed in-line, and when we see calls to things like Select, we replace them
    with the AST entries appropriate.

    ObjectStream has methods called Select and SelectMany. When they are called, they build up the AST tree. But they do that
    by creating Select and SelectMany, etc., ast nodes. When we parse a lambda passed as text, that does not happen. This
    NodeTransformer does that replacement in-place.
    '''

    def visit_Call(self, node):
        '''Look for LINQ type calls and make a replacement with the appropriate AST entry
        TODO: Make sure this is recursive properly!
        '''
        if type(node.func) is ast.Attribute:
            func_name =  node.func.attr
            if func_name == "Select":
                return query_ast.Select(node.func.value, wrap_lambda(node.args[0]))
            elif func_name == "SelectMany":
                return query_ast.SelectMany(node.func.value, wrap_lambda(node.args[0]))
        return node