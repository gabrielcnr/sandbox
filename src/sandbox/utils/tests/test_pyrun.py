import os
from typing import Dict

import pytest

from sandbox.utils import pyrun


def test_get_config_when_options_are_given_via_command_line():
    argv = "--sender=sender123 --recipients=recipient1,recipient2 --name=sometask foo.bar.baz -f -s".split()
    expected = {"sender": "sender123", "recipients": ["recipient1", "recipient2"],
                "name": "sometask", "script": "foo.bar.baz",
                "send_email_on_success": True, "send_email_on_failure": True, }
    assert expected == pyrun.get_config(argv=argv)


def test_get_config_when_options_are_given_via_environment_variables(mocker):
    mocker.patch.dict(os.environ, {"PYRUN_SENDER": "sender987",
                                   "PYRUN_RECIPIENTS": "r1@foo.com,r2@foo.com",
                                   "PYRUN_NAME": "myname",
                                   "PYRUN_FAILURE": "0",
                                   "PYRUN_SUCCESS": "1"})
    expected = {"sender": "sender987",
                "recipients": ["r1@foo.com", "r2@foo.com"],
                "name": "myname",
                "script": "foo.bar:baz",
                "send_email_on_failure": False,
                "send_email_on_success": True, }
    assert expected == pyrun.get_config(argv=["foo.bar:baz"])


def test_get_config_when_options_are_given_both_ways_cli_takes_precedence(mocker):
    argv = ("--sender=sender123 --recipients=recipient1,recipient2 "
            "--name=sometask foo.bar.baz -s").split()
    mocker.patch.dict(os.environ, {"PYRUN_SENDER": "sender987",
                                   "PYRUN_RECIPIENTS": "r1@foo.com,r2@foo.com",
                                   "PYRUN_NAME": "myname"})
    expected = {"sender": "sender123", "recipients": ["recipient1", "recipient2"],
                "name": "sometask", "script": "foo.bar.baz", "send_email_on_failure": False,
                "send_email_on_success": True}
    assert expected == pyrun.get_config(argv=argv)


@pytest.mark.parametrize(
    ["success", "failure", "returncode", "expected"],
    [
        (True, False, 0, True),
        (True, False, 1, False),

        (False, True, 0, False),
        (False, True, 1, True),

        (True, True, 0, True),
        (True, True, 1, True),

        (False, False, 0, False),
        (False, False, 1, False),
    ]
)
def test_should_send_email(success, failure, returncode, expected):
    assert pyrun.should_send_email(
        {"send_email_on_success": success, "send_email_on_failure": failure}, returncode) is expected


def test_format_dict():
    d = {"foo": 1, "barbarbar": 2, "hello": "world"}
    expected = """\
foo       : 1
barbarbar : 2
hello     : world"""
    assert expected == pyrun.format_dict(d)
