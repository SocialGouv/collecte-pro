# -*- coding: utf8 -*-

#doc : https://github.com/Peoplecantfly/icapserver

import time
import threading

from icapserver import *

class ICAPHandler(BaseICAPRequestHandler):

	def icap_OPTIONS(self):
		self.set_icap_response(200)
		self.set_icap_header('Methods', 'RESPMOD, REQMOD')
		self.set_icap_header('Service', 'ICAP Server' + ' ' + self._server_version)
		self.set_icap_header('Options-TTL', '3600')
		self.set_icap_header('Preview', '0')
		self.send_headers(False)

	def icap_REQMOD(self):
		self.no_adaptation_required()

	def icap_RESPMOD(self):
		print("respomoddde")
		self.set_icap_response(200)
		self.set_icap_header('Methods', 'RESPMOD, REQMOD')
		self.set_icap_header('Service', 'ICAP Server' + ' ' + self._server_version)
		self.set_icap_header('Options-TTL', '3600')
		self.set_icap_header('Preview', '0')
		self.send_headers(False)

class ICAPExampleServer():

	def __init__(self, addr='0.0.0.0', port=13440):
		self.addr = addr
		self.port = port

	def start(self):
            self.server = ICAPServer((self.addr, self.port), ICAPHandler)
            print(self.server)
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.start()
            return True

	def stop(self):
		self.server.shutdown()
		self.server.server_close()
		self.thread.join(2)
		return True


try:
    server = ICAPExampleServer()
    print("toto")
    server.start()
    print('Use Control-C to exit')
    while True:
        time.sleep(1)
except KeyboardInterrupt:
	server.stop()
	print('Finished')