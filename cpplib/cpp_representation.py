# The representation, in C++ code, of a particular variable.
# This is an abstract class. Almost everyone is going to have to
# implement one.
#
import xAODlib.statement as statement
from cpplib.cpp_vars import unique_name
import ast

class cpp_rep_base:
    r'''
    Represents a term or collection in C++ code. Queried to perform certian actions on the C++ term or collection.

    This is an abstract class for the most part. Do not override things that aren't needed - that way the system will
    know when the user tries to do something that they shouldn't have.
    '''
    def __init__(self):
        # Set to true when we represent an item in an interable type. 
        self.is_iterable = False
        self._ast = None

    def as_cpp(self):
        'Return the C++ code to represent whatever we are holding'
        raise BaseException("Subclasses need to implement in for as_cpp")

    def as_ast(self):
        'Return a python AST for this representation'
        if not self._ast:
            self.make_ast()
        return self._ast
    
    def make_ast(self):
        'Create and fill the _ast variable with the ast for this rep'
        raise BaseException("Subclasses need to implement this in as_ast")

class cpp_variable(cpp_rep_base):
    r'''
    The representation for a simple variable.
    '''

    def __init__(self, name, is_pointer=False, cpp_type = None):
        cpp_rep_base.__init__(self)
        self._cpp_name = name
        self._is_pointer = is_pointer
        self._cpp_type = cpp_type
        self._ast = None

    def name(self):
        return self._cpp_name

    def as_cpp(self):
        return self._cpp_name

    def is_pointer(self):
        return self._is_pointer

    def cpp_type(self):
        return self._cpp_type

    def make_ast(self):
        self._ast = ast.Name(self.as_cpp(), ast.Load())
        self._ast.rep = self

class cpp_expression(cpp_rep_base):
    r'''
    Represents a small bit of C++ code that is an expression. For example "a+b". It does not hold full
    statements.
    '''
    def __init__(self, expr, cpp_type=None):
        cpp_rep_base.__init__(self)
        self._expr = expr
        self._cpp_type = cpp_type

    def as_cpp(self):
        return self._expr

class cpp_collection(cpp_variable):
    r'''
    The representation for a collection. Something that can be iterated over.
    '''

    def __init__(self, name, is_pointer=False, cpp_type=None):
        r'''Remember the C++ name of this variable

        name - The name of the variable we are going to save here
        is_pointer - do we need to de-ref it to access it?
        '''
        cpp_variable.__init__(self, name, is_pointer, cpp_type=cpp_type)

    def loop_over_collection(self, gc):
        r'''
        Generate a loop over the collection

        gc - generated_code object to store code in

        returns:

        obj - term containing the object that is the loop variable
        '''

        # Create the var we are going to iterate over, and figure out how to reference
        # What we are doing.
        v = cpp_variable(unique_name("i_obj"), is_pointer=True)
        v.is_iterable = True
        c_ref = ("*" + self.name()) if self.is_pointer() else self.name()

        # Finally, the actual loop statement.
        gc.add_statement(statement.loop(c_ref, v.name()))

        # and that iterating variable is the rep
        return v
