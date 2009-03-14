#!/usr/bin/env python

# Use distutils as setuptools tries to be too smart and confuses
# everying.
from distutils.core import setup
from distutils import sysconfig

print sysconfig.get_config_var('prefix')

setup(
    name = "daneel-ai",
    version = "0.1.0",
    license = "GPL",
    description = "An advanced rule based AI for Thousand Parsec.",
    long_description = "",
    author = "Vincent Verhoeven",
    author_email = "verhoevenv@gmail.com",
    url = "http://www.thousandparsec.net",
    scripts = ["daneel-ai"],
    packages = ["daneel"],
    data_files = [("share/daneel-ai", ("LICENSE", "COPYING", "README")),
                  ("share/daneel-ai/rules/", ("rules/rfts", "rules/risk")),
                  ("share/tp/aiclients/", ("daneel-ai.xml",))],
)
