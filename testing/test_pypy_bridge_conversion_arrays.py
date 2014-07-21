from testing.test_interpreter import MockInterpreter, BaseTestInterpreter

import pytest

class TestPyPyBridgeArrayConversions(BaseTestInterpreter):

    # ------------------------
    # python list to php array
    # ------------------------
    def test_return_py_list_len(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return [1,2,3]
EOD;

embed_py_func($src);
$ar = f();
echo(count($ar));

        ''')
        assert phspace.int_w(output[0]) == 3


    def test_return_py_list_vals(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return [3, 2, 1]
EOD;

embed_py_func($src);
$ar = f();

for ($i = 0; $i < 3; $i++) {
    echo($ar[$i]);
}
        ''')
        for i in range(3):
            assert phspace.int_w(output[i]) == 3 - i

    def test_iter_vals_py_list_in_php(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return [3, 2, 1]
EOD;

embed_py_func($src);
$ar = f();

foreach ($ar as $i) {
    echo($i);
}
        ''')
        for i in range(3):
            assert phspace.int_w(output[i]) == 3 - i

    def test_iter_keys_vals_py_list_in_php(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return ["zero", "one", "two"]
EOD;

embed_py_func($src);
$ar = f();

foreach ($ar as $k => $v) {
    echo("$k:$v");
}
        ''')
        assert phspace.str_w(output[0]) == "0:zero"
        assert phspace.str_w(output[1]) == "1:one"
        assert phspace.str_w(output[2]) == "2:two"

    #------------------------------
    # Python dict to PHP array
    #------------------------------

    def test_return_py_dict_len(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return {"a" : "b", "c" : "d", "e" : "f"}
EOD;

embed_py_func($src);
$ar = f();
echo(count($ar));

        ''')
        assert phspace.int_w(output[0]) == 3

    def test_return_py_dict_vals_str_key(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return {"a" : "b", "c" : "d", "e" : "f"}
EOD;

embed_py_func($src);
$ar = f();
echo($ar["a"]);
echo($ar["c"]);
echo($ar["e"]);

        ''')
        assert phspace.str_w(output[0]) == "b"
        assert phspace.str_w(output[1]) == "d"
        assert phspace.str_w(output[2]) == "f"

    def test_return_py_dict_vals_int_key(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return {6 : "a", 7 : "b", 8 : "c"}
EOD;

embed_py_func($src);
$ar = f();
echo($ar[8]);
echo($ar[7]);
echo($ar[6]);

        ''')
        assert phspace.str_w(output[0]) == "c"
        assert phspace.str_w(output[1]) == "b"
        assert phspace.str_w(output[2]) == "a"

    def test_iter_vals_py_dict_in_php(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return {"x" : 10, 999 : 14, "z" : -1}
EOD;

embed_py_func($src);
$ar = f();

foreach ($ar as $i) {
    echo($i);
}
        ''')
        # ordering is that of python dict
        assert phspace.int_w(output[0]) == 10
        assert phspace.int_w(output[1]) == -1
        assert phspace.int_w(output[2]) == 14

    def test_iter_keys_vals_py_dict_in_php(self):
        phspace = self.space
        output = self.run('''

$src = <<<EOD
def f(): return {"x" : 10, 999 : 14, "z" : -1}
EOD;

embed_py_func($src);
$ar = f();

foreach ($ar as $k => $v) {
    echo("$k:$v");
}
        ''')
        # ordering is that of python dict
        assert phspace.str_w(output[0]) == "x:10"
        assert phspace.str_w(output[1]) == "z:-1"
        assert phspace.str_w(output[2]) == "999:14"

