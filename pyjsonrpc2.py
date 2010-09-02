# -*- coding: utf-8 -*-
# Specification:
# http://groups.google.com/group/json-rpc/web/json-rpc-1-2-proposal
#

# Server
import json
import logging
import traceback
try:
    from inspect import getcallargs
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

class JsonRPCSupport(object):
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
                return data['method'], data.get('params', []),data.get('id', None),not data.has_key('id')
                    
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
        data = {'jsonrpc': self.JSON_VERSION, 'method': method, 'id': None}
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

    def encode_result(self, result, reqid):
        return json.dumps({'jsonrpc': self.JSON_VERSION, 'result': result, 'id': reqid})

    def encode_error(self, code, error):
        return json.dumps({'jsonrpc': self.JSON_VERSION, 'error': {'code': code, 'message': error}})

class JsonRPCServer(object):
    input = None

    def __init__(self):
        self.support = JsonRPCSupport()

    def _response_error(self, input, code, message):
        # make error message
        _json = self.support.encode_error(code, message)
        logger.warn('Create error message => %s on incoming %s' % (_json, input))
        return _json

    def _working(self, input):
        kwargs = None
        args = None


        # validation structure of incoming json
        self.method, self.param, self.reqid, self.isnotify = self.support.decode_query(input)
            
        if type(self.method) is not unicode:
            logger.error('Method %s not unicode' % self.method)
            raise JsonInvalidRequest
        try:
            method = self.__getattribute__('do_%s' % self.method)
        except AttributeError:
            logger.error('Method %s not found' % self.method)
            raise JsonMethodNotFound
        if self.param:
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
        logger.debug('<-- INPUT: %s' % input)
        try:
            result = self._working(input)
            output = self.support.encode_result(result,self.reqid) if self.isnotify is False else u''
        except Exception as error:
            if hasattr(error, 'code') and hasattr(error, 'message'):
                output = self._response_error(input, error.code, error.message)
            else:
                logger.debug(traceback.print_exc())
                output = self._response_error(input, -32600, 'Invalid request')
        logger.debug('--> OUTPUT: %s' % output)
        
        return output


class JsonRPCClientBoundMethod(object):
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

class JsonRPCClient(object):
    def __init__(self, host):
        '''
            host - http://www.google.com/json/
        '''
        self.host = host

    def __getattr__(self, name):
        return JsonRPCClientBoundMethod(self, name)


