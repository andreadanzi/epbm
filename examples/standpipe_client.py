# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, os, csv, time, socket
import ConfigParser
import getopt
import logging
import logging.handlers

from datetime import datetime
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

#> twistd -ny standpipe_client.py
class Standpipe(DatagramProtocol):
    noisy = False
       
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

    def startProtocol(self):
        self.transport.connect(self.host, self.port) 
        self.sendDatagram()        

    def sendDatagram(self):
        self.logger.debug('sendDatagram')         
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
                self.transport.write("DATA:%d|%s|%f|%f|%f" % (self.sp_id,bh_id,delta_t,p_val,q_val), (self.host, self.port))
                time.sleep(0.1)
        self.logger.debug('sendDatagram terminated')
        
    def datagramReceived(self, datagram, (host, port)):
        self.logger.debug("Standpipe:datagramReceived %s from %s:%d" % (datagram,host, port))
        if datagram[:4] == "SYNC":
            inData = datagram[5:]
            self.logger.info("Standpipe:datagramReceived %s from %s:%d" % (inData,host, port))
            dtnow = datetime.utcnow()
            str_sync_rec = dtnow.strftime('%Y;%m;%d;%H;%M;%S;%f')            
            pongMsg = "OKSYNC " + sMsg
            self.transport.write(pongMsg, (host, port))
        if datagram[:5] == "START":
            self.logger.info("Standpipe:datagramReceived %s from %s:%d" % (datagram,host, port))
            self.sendDatagram()
        if datagram[:4] == "STOP":
            self.logger.info("Standpipe:datagramReceived %s from %s:%d" % (datagram,host, port))
            self.transport.write("STOP received", (host, port))
        if datagram[:6] == "STATUS":
            self.logger.info("Standpipe:datagramReceived %s from %s:%d" % (datagram,host, port))
            self.transport.write("STATUS received", (host, port))
        if datagram[:3] == "RES":
            self.logger.info("Standpipe:datagramReceived %s from %s:%d" % (datagram[4:],host, port))
      
                
             
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
        reactor.listenUDP(port+nStandpipe+1, protocol)
        reactor.run()
    
if __name__ == "__main__":
    main(sys.argv[1:])
