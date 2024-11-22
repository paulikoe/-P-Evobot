from socketIO_client import SocketIO, BaseNamespace

class Namespace(BaseNamespace):

    def on_connect(self):
        print('[Connected]')

def exec_code(args):
    exec(args['code'])
    print args['code']
    #print('on_response', args)


socketIO = SocketIO('159.203.69.117', 3000)
socketIO.emit('introduction', {'raspID': 'a'})
socketIO.on('exec code', exec_code)

socketIO.wait(seconds=60)