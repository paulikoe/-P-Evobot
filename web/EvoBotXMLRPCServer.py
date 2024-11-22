import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from syringe import Syringe
from head import Head
from datalogger import DataLogger

server = SimpleXMLRPCServer(('localhost', 9000), logRequests=True, allow_none=True)
server.register_introspection_functions()
server.register_multicall_functions()

syringes = []
usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )

for i in evobot.populatedSockets:
    for j in SYRINGES:
        if int(SYRINGES[j]['ID'])==int(i):
            syringe = Syringe( evobot, SYRINGES[j] )
            syringes.append( syringe )

for syringe in syringes:
    syringeMethods = [method for method in dir(syringe) if callable(getattr(syringe, method))]
    i = 0
    for method in syringeMethods:
        server.register_function( getattr( syringes[i], method ), "syringe" + str( i ) + str(method))
    i=i+1
        
evobotMethods = [method for method in dir(evobot) if callable(getattr(evobot, method))]

for method in evobotMethods:
    server.register_function( getattr( evobot, method ), "evobot" + str(method))

headMethods = [method for method in dir(head) if callable(getattr(head, method))]

for method in headMethods:
    server.register_function( getattr( head, method ), "head" + str(method))

            
try:
    print 'EvoBotServer now accepting requests (Use Control-C to stop server)'
    server.serve_forever()
except KeyboardInterrupt, SystemExit:
    print 'EvoBotServer finished'
