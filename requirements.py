#! /usr/bin/env python

# Preference the local directory first...
import sys
sys.path.insert(0, '.')
import os.path

# If we are working from git, initialise the submodules
modules = [("libtpproto-py", "tp.netlib"), ("libtpclient-py", "tp.client")] #, ("schemepy", "schemepy")]
if os.path.exists(".git"):
	for dir, name in modules:
		if os.path.exists(dir) and not os.path.exists(os.path.join(dir, ".git")):
			os.system("git submodule init")
	os.system("git submodule update")

for dir, name in modules:
	if os.path.exists(dir):
		sys.path.insert(0, dir)

# Check for our dependencies.
notfound = []
for dir, name in modules:
	try:
		exec("import %s as module" % name)

		print "%s version" % dir, module.__version__ 
		print "    (installed at %s)" % module.__installpath__

		try:
			exec("from %s.version import version_git" % name)
			print "    (git %s)" % version_git
		except ImportError:
			pass

	except (ImportError, KeyError, AttributeError), e:
		print e
		notfound.append(dir)
	print

if len(notfound) > 0:
	print "The following requirements where not met:"
	for module in notfound:
		print '    ', module
	print

if len(notfound) > 0:
	import sys
	sys.exit(1)

