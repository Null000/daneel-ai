#!/usr/bin/env python

# Use distutils as setuptools tries to be too smart and confuses
# everying.
from distutils.core import setup
from distutils import sysconfig

import shutil
import sys
import os.path

print sysconfig.get_config_var('prefix')

if sys.platform == 'win32':
    import py2exe
 
    if os.path.exists("dist"):
        shutil.rmtree("dist")
 
    if os.path.exists("tp"):
        shutil.rmtree("tp")
 
    shutil.copytree(os.path.join('libtpproto-py', 'tp', 'netlib'), os.path.join('tp', 'netlib'))
    shutil.copytree(os.path.join('libtpclient-py', 'tp', 'client'), os.path.join('tp', 'client'))
    open(os.path.join('tp', "__init__.py"), 'w').close()
 
    extra_arguments = dict(
        windows=[{
                "script": "daneel-ai",
        }],
        options={
                "py2exe": {
                        "dll_excludes": [],
                        "packages": ["tp.netlib", "tp.client"],
                        "optimize": 2,
                        "compressed": 0,
                }
        },
    )

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
    console = ["daneel-ai"],
    packages = ["daneel"],
    data_files = [("share/daneel-ai", ("LICENSE", "COPYING", "README")),
                  ("share/daneel-ai/rules/", ("rules/rfts", "rules/risk")),
                  ("share/tp/", ("daneel-ai.xml",))],
)
