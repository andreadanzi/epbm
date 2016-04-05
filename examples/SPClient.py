import logging
import logging.handlers
import sys
import SocketServer
import getopt
import sys, os, csv, time, socket
import ConfigParser
#danzi.tn@20160405 Simulazione Client su Cavalletto
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    )
                    
if __name__ == '__main__':
    import socket
    import threading
    sCFGName = 'mosul.cfg'
    mosulConfig = ConfigParser.RawConfigParser()
    mosulConfig.read(sCFGName)
    export_file = mosulConfig.get('DEMODATA','export_file')
    port = mosulConfig.getint('DEMODATA','port')
    server_host = mosulConfig.get('DEMODATA','server_host')
    argv = sys.argv[1:]
    nStandpipe = -1
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
    if nStandpipe >= 0:
        # logging
        logger = logging.getLogger('Client_%02d' % nStandpipe)
        logger.setLevel(logging.DEBUG)
        # create a rotating file handler which logs even debug messages 
        fh = logging.handlers.RotatingFileHandler('Client_%02d.log' % nStandpipe ,maxBytes=5000000, backupCount=5)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.debug('Send requests to server on %s:%s', server_host, port)  
        csvfile_name = "%s_%02d.csv" % ( export_file, nStandpipe)
        with open(csvfile_name) as csvfile:
            # Start_timestamp;delta_t;Project_ID;Domain_ID;Line_ID;Borehole_ID;Standpipe_ID;Stage_ID;Mix_ID;P;Q
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:    
                # Connect to the server
                logger.debug('creating socket')
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                logger.debug('connecting to server')
                s.connect((server_host, port))
                
                p_val = float(row["P"])
                q_val = float(row["Q"])
                delta_t = float(row["delta_t"])
                bh_id = row["Borehole_ID"]
                # Send the data
                message = "DATA:%02d|%s|%f|%f|%f" % (nStandpipe,bh_id,delta_t,p_val,q_val)
                logger.debug('sending data: "%s"', message)
                len_sent = s.send(message)

                # Receive a response
                logger.debug('waiting for response')
                response = s.recv(len_sent)
                logger.debug('response from server: "%s"', response)

                # Clean up
                logger.debug('closing socket')
                s.close()
                logger.debug('done')
                # 1 misura inviata al secondo
                time.sleep(1.0)
    print "Client Terminated"