# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, os, csv, time, socket
import ConfigParser
import getopt
import logging
import logging.handlers

from datetime import datetime
from twisted.internet import reactor, protocol

class StandpipeServer(protocol.Protocol):
       
    def m_init(self, host, port,  export_file):
        self.host = host
        self.port = port
        self.hostname = socket.gethostname()
        self.export_file = export_file
        self.oneRef = None
        self.logger = logging.getLogger('standpipe_server')
        self.logger.setLevel(logging.DEBUG)
        # create a rotating file handler which logs even debug messages 
        fh = logging.handlers.RotatingFileHandler('standpipe_server.log' ,maxBytes=5000000, backupCount=5)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.debug("StandpipeServer instance")
    
  
    def dataReceived(self, datagram, (host, port)):
        if datagram[:4] == "DATA":
            inData = datagram[5:]
            self.logger.info("StandpipeServer:datagramReceived %s from %s:%d" % (inData,host, port))    
            splitted = inData.split('|')
            v1 = float(splitted[-2])
            v2 = float(splitted[-1])
            res = v1*v2/10.
            self.transport.write("RES:%f" % res,(host, port))            
      
                
             
def main(argv):
    sCFGName = 'mosul.cfg'
    mosulConfig = ConfigParser.RawConfigParser()
    mosulConfig.read(sCFGName)
    sSyntax = os.path.basename(__file__) +" -n <stand_pipe_number> [-h for help]"
    try:
        opts, args = getopt.getopt(argv,"hn:",["number="])
    except getopt.GetoptError:
        print sSyntax
        sys.exit(1)
    if len(opts) < 1:
        print sSyntax
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print sSyntax
            sys.exit()          
    export_file = mosulConfig.get('DEMODATA','export_file')
    port = mosulConfig.getint('DEMODATA','port')
    server_host = mosulConfig.get('DEMODATA','server_host')
    factory = protocol.ServerFactory()
    factory.protocol = StandpipeServer()
    factory.protocol.m_init(server_host, port, export_file)
    reactor.listenTCP(port, factory)
    reactor.run()
    
if __name__ == "__main__":
    main(sys.argv[1:])
