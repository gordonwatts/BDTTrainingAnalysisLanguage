# Some tests to look at function simplifier

# Following two lines necessary b.c. I can't figure out how to get pytest to pick up the python path correctly
# despite reading a bunch of docs.
import sys
sys.path.append('.')

# Now the real test code starts.
from clientlib.function_simplifier import simplify_chained_calls
from clientlib.find_LINQ_operators import replace_LINQ_operators
import ast

class normalize_ast(ast.NodeTransformer):
    '''
    The AST's can have the same symantec meaning, but not the same text, so the string compare that happens as part of these tests fail. The code
    here's job is to make the ast produced by the local code look like the python code.
    '''
    def __init__ (self):
        self._arg_index = 0
        self._arg_transformer = []

    def push_stack_frame(self):
        self._arg_transformer.append({})

    def pop_stack_frame(self):
        del self._arg_transformer[-1]

    def new_arg(self):
        'Generate a new argument, in a nice order'
        old_arg = self._arg_index
        self._arg_index += 1
        return "arg_{0}".format(old_arg)

    def visit_Lambda(self, node):
        'Arguments need a uniform naming'
        a_mapping = [(a.arg, self.new_arg()) for a in node.args.args]

        # Remap everything that is inside this guy
        self.push_stack_frame()
        for m in a_mapping:
            self._arg_transformer[-1][m[0]] = m[1]
        body = self.visit(node.body)
        self.pop_stack_frame()

        # Rebuild the lambda guy
        args = [ast.arg(arg=m[1]) for m in a_mapping]
        return ast.Lambda(args=args, body=body)

    def visit_Name(self, node):
        id = node.id
        for frames in reversed(self._arg_transformer):
            if id in frames:
                return frames[id]
        return id


def util_process(ast_in, ast_out):
    'Make sure ast in is the same as out after running through - this is a utility routine for the harness'

    # Make sure the arguments are ok
    a_source = ast_in if isinstance(ast_in, ast.AST) else ast.parse(ast_in)
    a_expected = ast_out if isinstance(ast_out, ast.AST) else ast.parse(ast_out)

    a_source_linq = replace_LINQ_operators().visit(a_source)
    a_expected_linq = replace_LINQ_operators().visit(a_expected)

    a_updated = simplify_chained_calls().visit(a_source_linq)

    s_updated = ast.dump(normalize_ast().visit(a_updated))
    s_expected = ast.dump(normalize_ast().visit(a_expected_linq))

    assert s_updated == s_expected

################
# Test convolutions
def test_function_replacement():
    util_process('(lambda x: x+1)(z)', 'z+1')

def test_function_convolution_2deep():
    util_process('(lambda x: x+1)((lambda y: y)(z))', 'z+1')

def test_function_convolution_3deep():
    util_process('(lambda x: x+1)((lambda y: y)((lambda z: z)(a)))', 'a+1')

################
# Testing out Select from the start
#
def test_select_simple():
    # Select statement shouldn't be altered on its own.
    util_process("jets.Select(lambda j: j*2)", "jets.Select(lambda j: j*2)")

def test_select_select_convolution():
    util_process('jets.Select(lambda j: j).Select(lambda j2: j2*2)', 'jets.Select(lambda j2: j2*2)')

def test_select_identity():
    util_process('jets.Select(lambda j: j)', 'jets')

################
# Testing out SelectMany
def test_selectmany_simple():
    # SelectMany statement shouldn't be altered on its own.
    util_process("jets.SelectMany(lambda j: j.tracks)", "jets.SelectMany(lambda j: j.tracks)")

###############
# Testing first

################
# Tuple tests
def test_tuple_select():
    # (t1, t2)[0] should be t1.
    util_process('(t1,t2)[0]', 't1')

def test_tuple_in_lambda():
    util_process('(lambda t: t[0])((j1, j2))', 'j1')
def test_tuple_in_lambda_2deep():
    util_process('(lambda t: t[0])((lambda s: s[1])((j0, (j1, j2))))', 'j1')

def test_tuple_around_first():
    util_process('events.Select(lambda e: e.jets.Select(lambda j: (j, e)).First()[0])', 'events.Select(lambda e: e.jets.First())')