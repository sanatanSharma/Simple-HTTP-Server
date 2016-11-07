
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
import sys
import trace


statuses = {}
mapper = {}

ok_msg = "{'status':'ok'}"
kill_msg = "{'status':'killed'}"

# A custom exception
class NonExistentThread(Exception):

    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


# custom thread class for kiiling off a thread, extends Thread
class KThread(threading.Thread):

  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False

  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    threading.Thread.start(self)

  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup

  def globaltrace(self, frame, why, arg):
    if why == 'call':
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == 'line':
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True


# Threading class, extends python ThreadingMixIn, uses the custom thread class (KThread) for creating a thread
class Threading(ThreadingMixIn):

    daemon_threads = True

    def process_request(self, request, client_address):
        t = KThread(target = self.process_request_thread, args = (request, client_address))
        t.daemon = self.daemon_threads
        t.start()

# handles HTTP requests for the API  
class Handler(BaseHTTPRequestHandler):
    
    # GET request
    def do_GET(self):
        try:
            if self.path[5:12] == 'request':
                self.handlingGET()
            elif self.path[5:17] == 'serverStatus':
                self.getstatuses()
            else:
                raise Exception
        except SystemExit:
            self.send_error(500)
            return
        except:
            self.send_error(400)
            return
        return

    # PUT request
    def do_PUT(self):
        try:
            if self.path[5:9] == 'kill':
                self.killthethread()
            else:
                raise Exception
        except NonExistentThread as e:
            self.writetofile(e.value)
            return
        except:
            self.send_error(400)
            return
        return

    # kills off the required thread
    def killthethread(self):
        self.sendResponse(200)
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        tokill = int(content.split('=')[1][:-1])
        message = kill_msg
        if tokill in mapper:
            tobekilled = mapper[tokill]
        else:
            message = "{'status':'invalid connection Id "+str(tokill)+"'}"
            raise NonExistentThread(message)
            return
        tobekilled.kill()
        self.writetofile(kill_msg)
        del mapper[tokill]
        del statuses[tokill]
        self.writetofile(ok_msg)
        return

    # manages a GET request, get parametres, set statuses, run and close.
    def handlingGET(self):
        try:
            params = self.getparams()
            self.setstatuses(params)
            self.startrunning(params['timeOut'])
        except Exception:
            self.send_error(400)
            return
        del mapper[params['connID']]
        del statuses[params['connID']]
        self.sendResponse(200)
        self.writetofile(ok_msg)
        return

    #Get the parametres : connection ID and timeOut
    def getparams(self):
        conds = self.path.split('&')
        connID = int(conds[0].split('=')[1])
        timeOut = int(conds[1].split('=')[1])
        return {'connID':connID, 'timeOut':timeOut}
    
    # Running the loop for the specified time
    def startrunning(self, timeOut):
        self.timeleft = timeOut
        t_end = time.time() + timeOut
        while time.time() < t_end:
            self.timeleft = (t_end-time.time())/60
        return

    #Return the statuses of all the requests currently running on the server
    def getstatuses(self):
        message = '{'
        for connID, timevals in statuses.iteritems():
            timerem = round(timevals-time.time())
            message += '"'+str(int(connID))+'":"'+str(int(timerem))+'",'
        if message!='{':
            message = message[:-1]+"}"
        else:
            message+='}'
        self.sendResponse(200)
        self.writetofile(message)
        return

    # Sets up the global variable dicts : mapper and statuses
    def setstatuses(self, params):
        statuses[params['connID']] = time.time()+params['timeOut']
        mapper[params['connID']] = threading.currentThread()
        return



        # HELPER FUNCTIONS#
    def res(self, code, message):
        self.sendResponse(code)
        writetofile(message)
        return

    def writetofile(self, message):
        self.wfile.write(message)
        self.wfile.write('\n')
        return

    def sendResponse(self, code):
        self.send_response(code)
        self.end_headers()
        return


class ThreadedHTTPServer(Threading, HTTPServer):
    """Handle requests in a separate thread."""

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080

if __name__ == '__main__':
    server = ThreadedHTTPServer(('', port), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
