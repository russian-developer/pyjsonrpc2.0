#!/usr/bin/env python

import socket
import sys, os
import ConfigParser
from superfcgi.server import FastCGIMaster
from time import sleep
import logging


class Methods:
    def __init__(self, cfg):
        self.cfg = cfg
        try:
            self.pidfile = self.cfg.get('master', 'pidfile')
            self.sockfile = self.cfg.get('master', 'sockfile')
            self.workers = self.cfg.getint('master', 'workers')
            self.threads = self.cfg.getint('master', 'threads')
            self.logger_level = self.cfg.get('master', 'logger_level')
            self.logger_filename = self.cfg.get('master', 'logger_filename')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), e:
            print 'Hope error with parsing settings.cfg: %s' % e
            sys.exit()

    def start(self):
        logging.basicConfig(
#                    filename = self.logger_filename,
                    level = getattr(logging, self.logger_level),
                )
        try:
            f = open(self.pidfile, 'r')
            proc_id = int(f.read())
            f.close()
        except (IOError, ValueError):
            pass
        else:
            try:
                os.kill(proc_id, 0)
                sys.exit('Process allready runing')
            except OSError:
                pass
        print 'Start'
        try:
            os.remove(self.sockfile)
        except OSError:
            pass
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.sockfile)
        self.sock.listen(socket.SOMAXCONN)
        os.chmod(self.sockfile, 0777)
        if os.fork() > 0:
            os._exit(0)
        f = open(self.pidfile, 'w')
        f.write(str(os.getpid()))
        f.close()
        fcgi = FastCGIMaster(app='app.app', sock=self.sock,
                workers=self.workers, threads=self.threads)
        fcgi.start()

    def stop(self):
        print 'Stoping...'
        try:
            f = open(self.pidfile, 'r')
            proc_id = int(f.read())
            f.close()
        except (IOError, ValueError):
            print 'Process not runing'
        else:
            try:
                os.kill(proc_id, 15)
            except OSError, e:
                print 'Proccess not stoped with error %s' % e
            print 'Stoped worker'

    def restart(self):
        self.stop()
        print 'Sleep 1 seconds'
        sleep(1)
        self.start()

if __name__ == '__main__':
    METHODS = [method for method in Methods.__dict__.keys() if not method.startswith('_')]
    if len(sys.argv)<=1 or sys.argv[1] not in METHODS:
        sys.exit('Usage %s [%s]' % (sys.argv[0], '|'.join(METHODS)))
    if not os.access('settings.cfg', os.R_OK):
        sys.exit('Cannot read settings.cfg')
    print 'Try to %s' % sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.read('settings.cfg')
    methods_object = Methods(config)
    getattr(methods_object, sys.argv[1])()
