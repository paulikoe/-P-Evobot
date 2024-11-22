import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:9000')
print s.system.listMethods()
s.evobothome()
