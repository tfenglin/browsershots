#!/usr/bin/env python
# Get documentation from XML-RPC server with introspection
# Copyright (C) 2006 Johann C. Rocholl <johann@rocholl.net>
# Free software, licensed under the terms of the GNU GPL.
import sys, xmlrpclib
if len(sys.argv) != 2:
    print "usage: %s http://www.example.com/xmlrpc/" % sys.argv[0]
    sys.exit(1)
server = xmlrpclib.Server(sys.argv[1])
methods = server.system.listMethods()
methods.sort()
for method in methods:
    signatures = server.system.methodSignature(method)
    for signature in signatures:
        result = signature.pop(0)
        print "%s(%s) => %s" % (method, ', '.join(signature), result)
    doc = server.system.methodHelp(method)
    print '    ' + doc.replace('\n', '\n    ')
