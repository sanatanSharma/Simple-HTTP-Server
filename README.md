
### Socket HTTP Server providing APIs

The script is a basic server implementation which exposes three APIs. Uses python `SocketServer` and `BaseHTTPServer` libraries.
The SocketServer library provides framework for multi-threading (`ThreadingMixIn`) and the BaseHTTPServer provides framework for a simple server
and a Base HTTP request handler. The customized handler extends the Base HTTP Request handler and the requests are handled by creating functions by the name - `"do_<HTTP request name>"`.
A custom thread class (KThread) which extends the Thread class in library threading is used to kill off the threads.

### Prerequisities

Python 2.7

### Getting Started

Install Python 2.7 and run `server.py`.

### Usage

```sh
$ python server.py [port]
```

If port is unspecified the default port will be `8080`

-- To stop the server press `Ctrl+C`
### Sending Requests Examples

- GET API to run a request on the server:

```sh
$ curl -i 'http://localhost:8080/api/request?connId=12&timeout=4'
HTTP/1.0 200 OK
Server: BaseHTTP/0.3 Python/2.7.12
Date: Sat, 08 Oct 2016 09:01:51 GMT

{'status':'ok'}
```
`Format` - curl -i 'http://<IP address/ localhost>:<port>/api/request?connId=<some ID>&timeout=<some number>'

- GET API to get status: returns the `time remaining` of all the requests currently running on the server

```sh
$ curl -i 'http://localhost:8080/api/serverStatus'
HTTP/1.0 200 OK
Server: BaseHTTP/0.3 Python/2.7.12
Date: Sat, 08 Oct 2016 09:02:45 GMT

{"12":"7"}
```
`Format` - curl -i 'http://<IP address/ localhost>:<port>/api/serverStatus'

- PUT API : kills the request with the specified `connID`

```sh
$ curl -i -X PUT -d {"connId"=12} 'http://localhost:8080/api/kill'
HTTP/1.0 200 OK
Server: BaseHTTP/0.3 Python/2.7.12
Date: Sat, 08 Oct 2016 09:04:31 GMT

{'status':'killed'}
{'status':'ok'}
```
`Format` - curl -i -X PUT -d {"connId"=<some ID>} 'http://<IP address/ localhost>:<port>/api/kill'

### Possible error scenarios 

- Error Code `400` : Invalid format of the request/ invalid values, missing values of parameters like connId and timeout.
- Error Code `500` : A Running Request killed off.
