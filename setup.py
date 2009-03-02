#!/usr/bin/env python

from setuptools import setup

setup(
    name = "daneel-ai",
    version = "0.0.1",
    license = "GPL",
    description = "An advanced rule based AI for Thousand Parsec.",
    long_description = "",
    author = "Vincent Verhoeven",
    author_email = "verhoevenv@gmail.com",
    url = "http://www.thousandparsec.net",
    scripts = ["daneel-ai"],
    packages = ['.'],
    data_files = [(".", ("LICENSE", "COPYING", "README")),
                  ("rules", ("rules/rfts", "rules/risk"))],
)
