import logging
import sys
import SocketServer
import sys, os, csv, time, socket

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    )

class EchoRequestHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('EchoRequestHandler')
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

        # Echo the back to the client
        data = self.request.recv(1024)
        self.logger.debug('recv()->"%s"', data)
        self.request.send(data)
        return

    def finish(self):
        self.logger.debug('finish')
        return SocketServer.BaseRequestHandler.finish(self)

class EchoServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, handler_class=EchoRequestHandler):
        self.logger = logging.getLogger('EchoServer')
        self.logger.debug('__init__')
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        SocketServer.TCPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug('waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return SocketServer.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return SocketServer.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return SocketServer.TCPServer.close_request(self, request_address)

if __name__ == '__main__':
    import socket
    import threading

    address = ('localhost', 0) # let the kernel give us a port
    server = EchoServer(address, EchoRequestHandler)
    ip, port = server.server_address # find out what port we were given

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('client')
    logger.info('Server on %s:%s', ip, port)
    
    csvfile_name = "mosul_samples_04.csv"
    with open(csvfile_name) as csvfile:
        # Start_timestamp;delta_t;Project_ID;Domain_ID;Line_ID;Borehole_ID;Standpipe_ID;Stage_ID;Mix_ID;P;Q
        csv_reader = csv.DictReader(csvfile, delimiter=';')
        for row in csv_reader:    
            # Connect to the server
            logger.debug('creating socket')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug('connecting to server')
            s.connect((ip, port))

        
            p_val = float(row["P"])
            q_val = float(row["Q"])
            delta_t = float(row["delta_t"])
            bh_id = row["Borehole_ID"]
            # Send the data
            message = "DATA:%s|%s|%f|%f|%f" % ("04",bh_id,delta_t,p_val,q_val)
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
            time.sleep(0.1)
    server.socket.close()