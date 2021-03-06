# Test the cpp representations. These objects are quite simple, so there
# aren't that many tests. Mostly when bugs are found something gets added here.

# Following two lines necessary b.c. I can't figure out how to get pytest to pick up the python path correctly
# despite reading a bunch of docs.
import sys
sys.path.append('.')

import cpplib.cpp_representation as crep
import cpplib.cpp_types as ctyp
from xAODlib.util_scope import top_level_scope

def test_expression_pointer_decl():
    e2 = crep.cpp_value("dude", top_level_scope(), ctyp.terminal("int"))
    assert False == e2.is_pointer()

    e3 = crep.cpp_value("dude", top_level_scope(), ctyp.terminal("int", is_pointer=True))
    assert True == e3.is_pointer()
