#!/usr/bin/env python

import pycurl
import json
from cStringIO import StringIO

def curl(json):
    c = pycurl.Curl()
    c.setopt(pycurl.CONNECTTIMEOUT, 2)
    c.setopt(pycurl.TIMEOUT, 30)
    c.setopt(pycurl.NOSIGNAL, 1)
    c.body = StringIO()
    c.setopt(pycurl.URL, 'http://localhost:81/')
    c.setopt(pycurl.VERBOSE, 0)
    c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'User-Agent: Opera/9.22 (Windows NT 6.0; U; ru)'])
    c.setopt(pycurl.POSTFIELDS, json)
    c.setopt(pycurl.WRITEFUNCTION, c.body.write)
    c.perform()
    print '--> %s' % json
    print '<-- %s' % c.body.getvalue()


def now(q):
    for ii, i in enumerate(q):
        print '%s GET %s %s' % ('*'*8, ii,  '*'*8)
        curl(i)
        print '%s CORRECTS %s' % ('*'*8, '*'*8)
        for w in q[i]:
            print w

print """
--> {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
<-- {"jsonrpc": "2.0", "result": 19, "id": 1}

--> {"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}

<-- {"jsonrpc": "2.0", "result": -19, "id": 2}
rpc call with named parameters:
--> {"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}
<-- {"jsonrpc": "2.0", "result": 19, "id": 3}
--> {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}

<-- {"jsonrpc": "2.0", "result": 19, "id": 4}
a Notification:
--> {"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}
--> {"jsonrpc": "2.0", "method": "foobar"}
rpc call of non-existent method:
--> {"jsonrpc": "2.0", "method": "foobar", "id": "1"}
<-- {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Procedure not found."}, "id": "1"}
rpc call with invalid JSON:
--> {"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]
<-- {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error."}, "id": null}
rpc call with invalid Request object:
--> {"jsonrpc": "2.0", "method": 1, "params": "bar"}
<-- {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": null}
"""
q = {
        '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}': ['{"jsonrpc": "2.0", "result": 19, "id": 1}'],
        '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}': ['{"jsonrpc": "2.0", "result": -19, "id": 2}'],
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}': ['{"jsonrpc": "2.0", "result": 19, "id": 3}'],
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}': ['{"jsonrpc": "2.0", "result": 19, "id": 4}'],
        '{"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}': [],
        '{"jsonrpc": "2.0", "method": "foobar"}': [],
        '{"jsonrpc": "2.0", "method": "foobar", "id": "1"}': ['{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Procedure not found."}, "id": "1"}'],
        '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]': ['{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error."}, "id": null}'],
        '{"jsonrpc": "2.0", "method": 1, "params": "bar"}': ['{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": null}'],
    }

#now(q)

print '*' * 30
print '%s TESTING SPECIAL %s' % ('*' * 5, '*' * 5)
print '*' * 30

q = {
        '{"jsonrpc": "2.0", "method": "targs", "params": [1,2,3,4,5,6,7,8,9,10], "id": 1}': [],
        '{"jsonrpc": "2.0", "method": "tkwargs", "params": {"alfa": "1", "betta": "2", "gamma": "3"}, "id": 1}': [],
        '{"jsonrpc": "2.0", "method": "targs", "params": [1,2,3], "id": 1}': [],
        '{"jsonrpc": "2.0", "method": "targs", "params": [1,2], "id": 1}': [],
    }

now(q)

