#!/usr/bin/env python



"""
>>> from jsonlib import JsonRPCClient as Client
>>> link = Client('http://localhost:81/')
>>> link.none()
>>> link.args(1,2,3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.args(*[1,2,3])
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.kwargs(**{'alfa': 'ALFA', 'betta': 'BETTA', 'gamma': 'GAMMA'})
{u'jsonrpc': u'2.0', u'id': None, u'result': {u'alfa': u'ALFA', u'betta': u'BETTA', u'gamma': u'GAMMA'}}
>>> link.kwargs(alfa='ALFA', betta='BETTA', gamma='GAMMA')
{u'jsonrpc': u'2.0', u'id': None, u'result': {u'alfa': u'ALFA', u'betta': u'BETTA', u'gamma': u'GAMMA'}}
>>> link.args_and_kwargs(1,2,3,alfa='ALFA', betta='BETTA', gamma='GAMMA')
{u'jsonrpc': u'2.0', u'id': None, u'result': [[1, 2, 3], {u'alfa': u'ALFA', u'betta': u'BETTA', u'gamma': u'GAMMA'}]}
>>> link.args_and_kwargs(*[1,2,3], **{'alfa': 'ALFA', 'betta': 'BETTA', 'gamma': 'GAMMA'})
{u'jsonrpc': u'2.0', u'id': None, u'result': [[1, 2, 3], {u'alfa': u'ALFA', u'betta': u'BETTA', u'gamma': u'GAMMA'}]}
>>> link.args_and_kwargs(alfa='ALFA', betta='BETTA', gamma='GAMMA', *[1,2,3])
{u'jsonrpc': u'2.0', u'id': None, u'result': [[1, 2, 3], {u'alfa': u'ALFA', u'betta': u'BETTA', u'gamma': u'GAMMA'}]}
>>> link.args_and_kwargs(1,2,3,**{'alfa': 'ALFA', 'betta': 'BETTA', 'gamma': 'GAMMA'})
{u'jsonrpc': u'2.0', u'id': None, u'result': [[1, 2, 3], {u'alfa': u'ALFA', u'betta': u'BETTA', u'gamma': u'GAMMA'}]}
>>> link.named(1,2,3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.named(a=1, b=2, c=3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.named(**{'a': 1, 'b': 2, 'c': 3})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.named_with_default(1,2)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, False]}
>>> link.named_with_default(1,2,3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.named_with_default(*[1,2])
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, False]}
>>> link.named_with_default(*[1,2,3])
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.named_with_default(**{'a': 1,'b': 2,'c': 3})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3]}
>>> link.named_with_default(**{'a': 1,'b': 2})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, False]}
>>> link.named_with_args(1,2,3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, []]}
>>> link.named_with_args(1,2,3, *[1,2,3])
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [1, 2, 3]]}
>>> link.named_with_args(*[1,2,3], **{'a': 1, 'b': 2, 'c': 3})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [{u'a': 1, u'c': 3, u'b': 2}]]}
>>> link.named_with_args_and_kwargs(1,2,3, *[1,2,3], **{'aa': 1,'bb': 2,'cc': 3})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [1, 2, 3], {u'aa': 1, u'cc': 3, u'bb': 2}]}
>>> link.named_with_args_and_kwargs(*[1,2,3], **{'aa': 1, 'bb': 2, 'cc': 3})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [], {u'aa': 1, u'cc': 3, u'bb': 2}]}
>>> link.named_with_args_and_kwargs(*[1,2,3], **{'aa': 1, 'bb': 2, 'cc': 3, 'd': 4})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [], {u'aa': 1, u'cc': 3, u'd': 4, u'bb': 2}]}
>>> link.named_with_args_and_kwargs(**{'a': 1, 'b': 2, 'c': 3, 'd': 4})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [], {u'd': 4}]}
>>> link.named_with_args_and_kwargs(1,2,3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, [], {}]}
>>> link.named_with_default_and_args(1,2, *[1,2,3])
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 1, [2, 3]]}
>>> link.named_with_default_and_args(1,2)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, False, []]}
>>> link.named_with_default_and_args(1,2,3)
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, []]}
>>> link.named_with_default_and_args(**{'a': 1,'b': 2,'c': 3})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, 3, []]}
>>> link.named_with_default_and_args(**{'a': 1,'b': 2})
{u'jsonrpc': u'2.0', u'id': None, u'result': [1, 2, False, []]}
"""


if __name__ == '__main__':
    import doctest
    doctest.testmod()
