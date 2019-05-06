import os
import pytest
import unittest

from expandvars import expandvars


def test_expandvars_constant():
    os.environ.update({"FOO": "bar"})
    assert expandvars("FOO") == "FOO"
    assert expandvars("$") == "$"
    assert expandvars("BAR$") == "BAR$"
    assert expandvars("B$AR") == "B$AR"


def test_expandvars_empty():
    if "foo" in os.environ:
        del os.environ["foo"]
    assert expandvars("$foo") == ""


def test_expandvars_simple():
    os.environ.update({"FOO": "bar", "BIZ": "buz"})
    assert expandvars("$FOO") == "bar"
    assert expandvars("${FOO}") == "bar"
    assert expandvars("${FOO}:$BIZ") == "bar:buz"


def test_expandvars_get_default():
    if "FOO" in os.environ:
        del os.environ["FOO"]
    assert expandvars("${FOO:-default}") == "default"
    assert expandvars("${FOO:-}") == ""


def test_expandvars_update_default():
    if "FOO" in os.environ:
        del os.environ["FOO"]
    assert expandvars("${FOO:=}") == ""
    del os.environ["FOO"]
    assert expandvars("${FOO:=default}") == "default"
    assert os.environ.get("FOO") == "default"
    assert expandvars("${FOO:=ignoreme}") == "default"


def test_expandvars_substitute():
    if "BAR" in os.environ:
        del os.environ["BAR"]
    os.environ.update({"FOO": "bar"})
    assert expandvars("${FOO:+foo}") == "foo"
    assert expandvars("${BAR:+foo}") == ""
    assert expandvars("${BAR:+}") == ""


def test_offset():
    os.environ.update({"FOO": "damnbigfoobar"})
    assert expandvars("${FOO:3}") == "nbigfoobar"
    assert expandvars("${FOO: 4}") == "bigfoobar"
    assert expandvars("${FOO:30}") == ""
    assert expandvars("${FOO:0}") == "damnbigfoobar"
    assert expandvars("${FOO:foo}") == "damnbigfoobar"


def test_offset_length():
    os.environ.update({"FOO": "damnbigfoobar"})
    assert expandvars("${FOO:4:3}") == "big"
    assert expandvars("${FOO: 7:6}") == "foobar"
    assert expandvars("${FOO:7: 100}") == "foobar"
    assert expandvars("${FOO:0:100}") == "damnbigfoobar"
    assert expandvars("${FOO:70:10}") == ""
    assert expandvars("${FOO:1:0}") == ""
    assert expandvars("${FOO:0:}") == ""
    assert expandvars("${FOO:0:foo}") == ""
    assert expandvars("${FOO::}") == ""
    assert expandvars("${FOO::5}") == "damnb"


def test_invalid_length_err():
    os.environ.update({"FOO": "damnbigfoobar"})
    with pytest.raises(ValueError) as e:
        expandvars("${FOO:1:-3}")
        assert e.value == "-3: substring expression < 0"


def test_bad_syntax_err():
    os.environ.update({"FOO": "damnbigfoobar"})
    with pytest.raises(ValueError) as e:
        expandvars("${FOO:}") == ""
        assert e.value == "bad substitution"


def test_invalid_operand_err():
    os.environ = {"FOO": "damnbigfoobar"}
    oprnds = "@#$%^&*()_'\"\\"
    for o in oprnds:
        with pytest.raises(ValueError) as e:
            expandvars("${{FOO:{}}}".format(o))
            assert e.value == (
                "FOO: {}: syntax error: operand expected (error token is {})"
            ).format(o, repr(o))

        with pytest.raises(ValueError) as e:
            expandvars("${{FOO:0:{}}}".format(o))
            assert e.value == (
                "FOO: {}: syntax error: operand expected (error token is {})"
            ).format(o, repr(o))