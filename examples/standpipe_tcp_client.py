# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, os, csv, time, socket
import ConfigParser
import getopt
import logging
import logging.handlers

from datetime import datetime
from twisted.internet import reactor, protocol

class Standpipe(protocol.Protocol):
       
    def m_init(self, host, port, sp_id, export_file):
        self.host = host
        self.port = port
        self.hostname = socket.gethostname()
        self.sp_id = sp_id
        self.export_file = export_file
        self.oneRef = None
        self.logger = logging.getLogger('standpipe_client_%02d' % self.sp_id)
        self.logger.setLevel(logging.DEBUG)
        # create a rotating file handler which logs even debug messages 
        fh = logging.handlers.RotatingFileHandler('standpipe_client_%02d.log' % self.sp_id ,maxBytes=5000000, backupCount=5)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.debug("Standpipe instance %02d" % self.sp_id)

    """Once connected, send a message, then print the result."""
    def connectionMade(self):
        self.logger.debug('connectionMade')         
        csvfile_name = "%s_%02d.csv" % ( self.export_file, self.sp_id)
        with open(csvfile_name) as csvfile:
            # Start_timestamp;delta_t;Project_ID;Domain_ID;Line_ID;Borehole_ID;Standpipe_ID;Stage_ID;Mix_ID;P;Q
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:
                # time.sleep(1)
                p_val = float(row["P"])
                q_val = float(row["Q"])
                delta_t = float(row["delta_t"])
                bh_id = row["Borehole_ID"]
                self.logger.debug("sent %s|%f|%f|%f"%(bh_id,delta_t,p_val,q_val))
                self.transport.write("DATA:%d|%s|%f|%f|%f" % (self.sp_id,bh_id,delta_t,p_val,q_val))
                time.sleep(0.1)
        self.logger.debug('connectionMade terminated')
    
    def dataReceived(self, data):
        if data[:3] == "RES":
            self.logger.info("Standpipe:datagramReceived ", data)        
    
    def connectionLost(self, reason):
        print "connection lost"        
        
class StandpipeFactory(protocol.ClientFactory):
    protocol = Standpipe

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()        
      
                
             
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
        elif opt in ("-n", "--number"):
            nStandpipe = int(arg)
          
            
    if nStandpipe:
        export_file = mosulConfig.get('DEMODATA','export_file')
        port = mosulConfig.getint('DEMODATA','port')
        server_host = mosulConfig.get('DEMODATA','server_host')
        protocol = Standpipe()
        protocol.m_init(server_host, port, nStandpipe,export_file)
        reactor.listenUDP(port, protocol)
        reactor.run()
    
if __name__ == "__main__":
    main(sys.argv[1:])
