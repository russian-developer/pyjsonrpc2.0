# -*- coding: utf-8 -*-
# Specification:
# http://groups.google.com/group/json-rpc/web/json-rpc-1-2-proposal
#

# Server
import json
import logging
import traceback
#import inspect
try:
    from inspcet import getcallargs
except ImportError:
    from inspector import getcallargs

# Client
import urllib2





logger = logging.getLogger(__name__)

class JsonInvalidRequest(Exception):
    code = -32600
    message = u'Invalid request'

class JsonInvalidParams(Exception):
    code = -32602
    message = u'Invalid params'

class JsonMethodNotFound(Exception):
    code = -32601
    message = u'Method not found'

class JsonParseError(Exception):
    code = -32700
    message = u'Parse error'

class JsonInternalError(Exception):
    code = -32603
    message = u'Internal error'


ErrorClasses = [JsonInvalidRequest, JsonInvalidParams, JsonMethodNotFound,
        JsonParseError, JsonInternalError]

class JsonRPCSupport:
    JSON_VERSION = '2.0'

    def _decode(self, data):
        if len(data)>1:
            try:
                data = json.loads(data)
            except ValueError:
                logger.exception('Cannot decode gived json data')
                raise JsonParseError
            return data
        return None


    def decode_query(self, data):
        data = self._decode(data)
        if data:
            try:
                return data['method'], data.get('params', [])
            except KeyError:
                logger.exception('Cannot find method name')
                raise JsonInvalidRequest

    def decode_result(self, data):
        data = self._decode(data)
        if data:
            try:
                return data['result']
            except KeyError:
                logger.exception('Cannot find result key')
                raise JsonParseError

    def decode_error(self, data):
        data = self._decode(data)
        if data:
            try:
                error = data['error']
                return error['code'], error['message']
            except KeyError:
                logger.exception('Cannot find error code or eror message')
                raise JsonParseError

    def encode_query(self, method, *args, **kwargs):
        param = None
        data = {'jsonrpc': self.JSON_VERSION, 'method': method}
        args = list(args)
        if args:
            param = args
        if kwargs:
            if args:
                param.append(kwargs)
            else:
                param = kwargs
        if param:
            data['params'] = param
        return json.dumps(data)

    def encode_result(self, result):
        if result:
            data = {'jsonrpc': self.JSON_VERSION, 'result': result}
            return json.dumps(data)
        return

    def encode_error(self, code, error):
        data = {'jsonrpc': self.JSON_VERSION, 'error': {'code': code, 'message': error}}
        return json.dumps(data)

class JsonRPCServer(object):
#    id = None
    input = None

    def __init__(self):
        self.support = JsonRPCSupport()

    def _response_error(self, code, message):
        # make error message
        _json = self.support.encode_error(code, message)
        logger.warn('Create error message => %s on incoming %s' % (_json, self.input))
        return _json

    def _working(self):
        kwargs = None
        args = None


        # validation structure of incoming json
        self.method, self.param = self.support.decode_query(self.input)
        if type(self.method) is not unicode:
            logger.error('Method %s not unicode' % self.method)
            raise JsonInvalidRequest
        try:
            method = self.__getattribute__('do_%s' % self.method)
        except AttributeError:
            logger.error('Method %s not found' % self.method)
            raise JsonMethodNotFound
        if self.param:
            logger.warn('PARAMS -> %s' % self.param)
            if isinstance(self.param, str):
                try:
                    getcallargs(method, *[self.param])
                    args = [self.param]
                except TypeError:
                    logger.exception('Invalid params')
                    raise JsonInvalidParams
            elif isinstance(self.param, dict):
                try:
                    getcallargs(method, **self.param)
                    kwargs = self.param
                except TypeError:
                    logger.exception('Invalid params')
                    raise JsonInvalidParams
            elif isinstance(self.param, list):
                if isinstance(self.param[-1], dict):
                    try:
                        getcallargs(method, *self.param[:-1], **self.param[-1])
                        args = self.param[:-1]
                        kwargs = self.param[-1]
                    except TypeError:
                        logger.exception('Invalid params')
                if not args and not kwargs:
                    try:
                        getcallargs(method, *self.param)
                        args = self.param
                    except TypeError:
                        logger.exception('Invalid param')
                        raise JsonInvalidParams

#
#        arg_names, args_name, kwargs_name, defaults = \
#                                                inspect.getargspec(method)
#        assert arg_names[0]=='self'
#        arg_names = arg_names[1:]
#        param_type = type(self.param)
#        if defaults:
#            important_args = arg_names[:len(arg_names)-len(defaults)]
#        else:
#            important_args = arg_names
#
#        if param_type is str:
#            if len(arg_names) == 1 or args_name:
#                args = [self.param]
#            else:
#                raise JsonInvalidParams
#        elif param_type is dict:
#            for arg in important_args:
#                if arg not in self.param.keys():
#                    # Gived kwargs not contains important key
#                    logger.error('Gived kwargs %s not contains important \
#                            key %s in %s' % (self.param.keys(), arg, important_args))
#                    raise JsonInvalidParams
#            if not kwargs_name:
#                for key in self.param.keys():
#                    if key not in arg_names:
#                        # Gived kwargs contain unknown key
#                        logger.error('Gived kwargs %s contain unknown \
#                                key %s in %s' % (self.param.keys(), key, arg_names))
#                        raise JsonInvalidParams
#            kwargs = self.param
#        elif param_type is list:
#            try:
#                last_param = self.param[-1]
#                last_param_type = type(last_param)
#            except IndexError:
#                last_param_type = None
#            if not args_name and not kwargs_name:
#                if len(important_args)>len(self.param) or len(arg_names)<len(self.param):
#                    # Given more or less parameters
#                    logger.error('Gived %s but important %s args and %s \
#                            available parameters' % (len(important_args), len(args_name), len(self.param)))
#                    raise JsonInvalidParams
#                else:
#                    args = self.param
#
#            if args_name and not kwargs_name:
#                if len(important_args)>len(self.param):
#                    # Given less parameters
#                    logger.error('Gived %s but expected %s parameters [%s/%s]' % (len(important_args), 
#                        len(self.param), important_args, self.param))
#                    raise JsonInvalidParams
#                args = self.param
#            if not args_name and kwargs_name:
#                if last_param_type is dict:
#                    if len(important_args) > len(self.param[:-1]):
#                        args = self.param
#                        if len(important_args) > len(self.param) or len(arg_names) < len(self.prarm[:-1]):
#                            # Given more or less parameters
#                            logger.error('Gived %s but important %s args and %s \
#                                    available parameters' % (len(important_args), len(args_name), len(self.param[:-1])))
#                            raise JsonInvalidParams
#                    else:
#                        kwargs = last_param
#                        args = self.param[:-1]
#                else:
#                    if len(important_args) > len(self.param) or len(arg_names) < len(self.param):
#                        # Given more or less parameters
#                        logger.error('Gived %s but important %s args and %s \
#                                available parameters' % (len(important_args), len(args_name), len(self.param)))
#                        raise JsonInvalidParams
#                    args = self.param
#            if args_name and kwargs_name:
#                if last_param_type is dict:
#                    if len(important_args) > len(self.param[:-1]):
#                        args = self.param
#                        if len(important_args) > len(self.param):
#                            # Given less parameters
#                            logger.error('Gived %s but expected %s parameters' % (len(important_args), len(self.param)))
#                            raise JsonInvalidParams
#                    else:
#                        kwargs = last_param
#                        args = self.param[:-1]
#                else:
#                    if len(important_args) > len(self.param):
#                        # Given less parameters
#                        logger.error('Gived %s but expected %s parameters' % (len(important_args), len(self.param)))
#                        raise JsonInvalidParams
#                    args = self.param

        try:
            if args and kwargs:
                return method(*args, **kwargs)
            elif args:
                return method(*args)
            elif kwargs:
                return method(**kwargs)
            else:
                return method()
        except:
            logger.exception('Hope internal error')
            raise JsonInternalError



    def __call__(self, input):
        self.input = input
        logger.debug('<-- INPUT: %s' % self.input)
        try:
            result = self._working()
            if result:
                result = self.support.encode_result(result)
            else:
                return u''
        except Exception as error:
            if hasattr(error, 'code') and hasattr(error, 'message'):
                result = self._response_error(error.code, error.message)
            else:
                logger.debug(traceback.print_exc())
                result = self._response_error(-32600, 'Invalid request')
        logger.debug('--> OUTPUT: %s' % result)
        
        return result


class JsonRPCClientBoundMethod:
    def __init__(self, instance, function):
        self.function = function
        self.instance = instance
        self.support = JsonRPCSupport()

    def __call__(self, *args, **kwargs):
        encoded_data = self.support.encode_query(self.function, *args, **kwargs)
        request = urllib2.Request(
                url=self.instance.host,
                data=encoded_data,
                )
        request.add_header('Content-Type', 'application/json')
        link = urllib2.urlopen(request)
        data = link.read()
        try:
            return self.support.decode_result(data)
        except JsonParseError:
            code, error = self.support.decode_error(data)
            for err in ErrorClasses:
                if err.code == code:
                    logger.error('Generation error with %s/%s' % (code, error))
                    raise err

class JsonRPCClient:
    def __init__(self, host):
        '''
            host - http://www.google.com/json/
        '''
        self.host = host

    def __getattr__(self, name):
        return JsonRPCClientBoundMethod(self, name)


