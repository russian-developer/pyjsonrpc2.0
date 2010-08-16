# -*- coding: utf-8 -*-
# Specification:
# http://groups.google.com/group/json-rpc/web/json-rpc-1-2-proposal
#

# Server
import json
import logging
import traceback
import inspect

# Client
import urllib2



JSON_VERSION = {'jsonrpc': '2.0'}


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


class JsonRPCServer(object):
    id = None
    input = None

    def request(self):
        _json = self._decode(self.input)
        return _json.get('method', None), _json.get('params', []), _json.get('id', None)

    def _encode(self, *args):
        # convert dict to json use JSON 2.0 specification
        data_dict = JSON_VERSION.copy()
        data_dict.update({'id': self.id})
        for arg in args:
            data_dict.update(arg)
        return json.dumps(data_dict)

    def _decode(self, data):
        try:
            return json.loads(data)
        except ValueError:
            self.id = None
            raise JsonParseError

    def _response_error(self, code, message):
        # make error message
        _json = self._encode({'error': {'code': code, 'message': message}})
        logger.warn('Create error message => %s on incoming %s' % (_json, self.input))
        return _json

    def _working(self):
        kwargs = None
        args = None


        # validation structure of incoming json
        self.method, self.param, self.id = self.request()
        if type(self.method) is not unicode:
            logger.error('Method %s not unicode' % self.method)
            raise JsonInvalidRequest
        try:
            method = self.__getattribute__('do_%s' % self.method)
        except AttributeError:
            logger.error('Method %s not found' % self.method)
            raise JsonMethodNotFound

        arg_names, args_name, kwargs_name, defaults = \
                                                inspect.getargspec(method)
        assert arg_names[0]=='self'
        arg_names = arg_names[1:]
        param_type = type(self.param)
        if defaults:
            important_args = arg_names[:len(arg_names)-len(defaults)]
        else:
            important_args = arg_names

        if param_type is str:
            if len(arg_names) == 1 or args_name:
                args = [self.param]
            else:
                raise JsonInvalidParams
        elif param_type is dict:
            for arg in important_args:
                if arg not in self.param.keys():
                    # Gived kwargs not contains important key
                    logger.error('Gived kwargs %s not contains important \
                            key %s in %s' % (self.param.keys(), arg, important_args))
                    raise JsonInvalidParams
            if not kwargs_name:
                for key in self.param.keys():
                    if key not in arg_names:
                        # Gived kwargs contain unknown key
                        logger.error('Gived kwargs %s contain unknown \
                                key %s in %s' % (self.param.keys(), key, arg_names))
                        raise JsonInvalidParams
            kwargs = self.param
        elif param_type is list:
            try:
                last_param = self.param[-1]
                last_param_type = type(last_param)
            except IndexError:
                last_param_type = None
            if not args_name and not kwargs_name:
                if len(important_args)>len(self.param) or len(arg_names)<len(self.param):
                    # Given more or less parameters
                    logger.error('Gived %s but important %s args and %s \
                            available parameters' % (len(important_args), len(args_name), len(self.param))
                    raise JsonInvalidParams
                else:
                    args = self.param

            if args_name and not kwargs_name:
                if len(important_args)>len(self.param):
                    # Given less parameters
                    logger.error('Gived %s but expected %s parameters' % (len(important_args), len(self.param))
                    raise JsonInvalidParams
                args = self.param
            if not args_name and kwargs_name:
                if last_param_type is dict:
                    if len(important_args) > len(self.param[:-1]):
                        args = self.param
                        if len(important_args) > len(self.param) or len(arg_names) < len(self.prarm[:-1]):
                            # Given more or less parameters
                            logger.error('Gived %s but important %s args and %s \
                                    available parameters' % (len(important_args), len(args_name), len(self.param[:-1]))
                            raise JsonInvalidParams
                    else:
                        kwargs = last_param
                        args = self.param[:-1]
                else:
                    if len(important_args) > len(self.param) or len(arg_names) < len(self.param):
                        # Given more or less parameters
                        logger.error('Gived %s but important %s args and %s \
                                available parameters' % (len(important_args), len(args_name), len(self.param))
                        raise JsonInvalidParams
                    args = self.param
            if args_name and kwargs_name:
                if last_param_type is dict:
                    if len(important_args) > len(self.param[:-1]):
                        args = self.param
                        if len(important_args) > len(self.param):
                            # Given less parameters
                            logger.error('Gived %s but expected %s parameters' % (len(important_args), len(self.param))
                            raise JsonInvalidParams
                    else:
                        kwargs = last_param
                        args = self.param[:-1]
                else:
                    if len(important_args) > len(self.param):
                        # Given less parameters
                        logger.error('Gived %s but expected %s parameters' % (len(important_args), len(self.param))
                        raise JsonInvalidParams
                    args = self.param

        try:
            if args and kwargs:
                return method(*args, **kwargs)
            elif args:
                return method(*args)
            elif kwargs:
                return method(**kwargs)
        except:
            logger.exception('Hope internal error')
            raise JsonInternalError



    def __call__(self, input):
        self.input = input
        logger.debug('<-- INPUT: %s' % self.input)
        try:
            result = self._working()
            if result:
                result = self._encode({'result': result})
            else:
                return
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

    def __call__(self, *args, **kwargs):
        params = None
        mask = JSON_VERSION.copy()
        mask['method'] = self.function
        if args:
            params = list(args)
            if kwargs:
                params.append(kwargs)
        elif kwargs:
            params = kwargs
        if params:
            mask['params'] = params
        request_data = json.dumps(mask)
        request = urllib2.Request(
                url=self.instance.host,
                data=request_data,
                )
        request.add_header('Content-Type', 'application/json')
        link = urllib2.urlopen(request)
        data = link.read()
        try:
            response = json.loads(data)
        except ValueError:
            return
        if response.has_key('error'):
            for error in ErrorClasses:
                if error.code == response['error']['code']:
                    print response['error']['message']
                    raise error
        return response

class JsonRPCClient:
    def __init__(self, host):
        '''
            host - http://www.google.com/json/
        '''
        self.host = host

    def __getattr__(self, name):
        return JsonRPCClientBoundMethod(self, name)


