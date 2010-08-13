import random
import logging
from jsonlib import JsonRPCServer

logger = logging.getLogger(__name__)

class Methods(JsonRPCServer):
    def do_none(self):
        pass

    def do_args(self, *args):
        return args

    def do_kwargs(self, **kwargs):
        return kwargs

    def do_args_and_kwargs(self, *args, **kwargs):
        return args, kwargs

    def do_named(self, a, b, c):
        return a,b,c

    def do_named_with_default(self, a, b, c=False):
        return a,b,c

    def do_named_with_args(self, a, b, c, *args):
        return a,b,c,args

    def do_named_with_args_and_kwargs(self, a, b, c, *args, **kwargs):
        return a,b,c,args,kwargs

    def do_named_with_default_and_args(self, a, b, c=False, *args):
        return a,b,c,args

    def do_internal(self):
        raise


class Handler:
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, env, start_response):
        input = env['wsgi.input'].readline()
        content_type = env.get('CONTENT_TYPE', None)
        if content_type != 'application/json':
            logger.warn('Request with bad content type %s' % content_type)
            start_response('501', [('Content-type', 'text/html')])
            return ['Please use application/json type only\n']
        start_response('200 OK', [('Content-type', 'application/json')])
        return ['%s\n' % self.methods(input)]


app = Handler(Methods())
