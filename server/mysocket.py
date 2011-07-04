#!/usr/bin/env python
# coding: utf-8
"""
    socket functions for mycloud server

    Copyright (C) 2010  Pan, Shi Zhu

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import sys
import socket

DEFAULT_PORT = 10007
BUFSIZE = 1024
verbose = False

# sample server func
def sample_server_func(indata):
    if indata == 'close':
        return None  # to shutdown the server
    elif indata == 'disconnect':
        return 0     # to disconnect
    elif indata == 'hello':
        return "acknowledgement"
    else:
        return "ignored"

def tcpslice(sendfunc, data):
    senddata = data
    while len(senddata) >= BUFSIZE:
        sendfunc(senddata[0:BUFSIZE])
        senddata = senddata[BUFSIZE:]
    if senddata[-1:] == "\n":
        sendfunc(senddata)
    else:
        sendfunc(senddata+"\n")

def tcpserver(func, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(1)
    name = 'tcp server'
    try:
        s.bind(('', port))
    except Exception, inst:
        s.close()
        if verbose:
            print name, "start fail:", type(inst).__name__, inst
        return
    if verbose:
        print name,'at port', port
    server_close = False
    try:
        while True:
            s.listen(1)                 # 服务器的侦听连接
            conn, addr = s.accept()     # 接收一个新的 tcp 连接会话
            if verbose:
                print name,'connected to', addr
            cachedata = ""
            while True:
                data = conn.recv(BUFSIZE)
                if not data:
                    break
                if data[-1:] == "\n":
                    data = cachedata + data[:-1]
                    cachedata = ""
                else:
                    cachedata += data
                    continue
                if verbose:
                    print name,'received:', data
                if func:
                    try:
                        ret = func(data)
                    except Exception, inst:
                        if verbose:
                            print name, type(inst).__name__, ":", inst
                        conn.send('\n')
                        break
                    if ret == None:
                        conn.send('server closed\n')
                        server_close = True
                        break
                    elif ret == 0:
                        break
                    elif type(ret).__name__ == "str":
                        if verbose:
                            print name, 'send data ',len(ret),'bytes'
                        tcpslice(conn.send, ret)
                    else:
                        senddata = str(ret)
                        if verbose:
                            print name,'send data ',len(senddata),'bytes'
                        tcpslice(conn.send, senddata)
                else:
                    conn.send('\n')
            conn.close()                # 关闭该 tcp 连接
            if verbose:
                print name,'closed connection to', addr
            if server_close:            # 关闭服务器的侦听连接
                break
    except BaseException, inst:
        print name, type(inst).__name__, ":", inst
    finally:
        s.close()
        if verbose:
            print name, "exit"

def udpslice(sendfunc, data, addr):
    senddata = data
    while len(senddata) >= BUFSIZE:
        sendfunc(senddata[0:BUFSIZE], addr)
        senddata = senddata[BUFSIZE:]
    if senddata[-1:] == "\n":
        sendfunc(senddata, addr)
    else:
        sendfunc(senddata+"\n", addr)

def udpserver(func, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(1)
    name = 'udp server'
    try:
        s.bind(('', port))
    except Exception, inst:
        s.close()
        print name, "start fail:", inst
        return
    print name,'on port', port
    while True:
        data, addr = s.recvfrom(BUFSIZE)
        data = data[:-1]
        print name,'received from %r: %s' % (addr, data)
        if func:
            try:
                ret = func(data)
            except Exception:
                s.sendto('\n', addr)
                continue
            if ret == None:
                s.sendto('server closed\n', addr)
                break
            elif ret == 0:
                pass
            elif type(ret).__name__ == "str":
                print name,'send data',len(ret),'bytes'
                udpslice(s.sendto, ret, addr)
            else:
                senddata = str(ret)
                print name,'send data',len(senddata),'bytes'
                udpslice(s.sendto, senddata, addr)
        else:
            s.sendto('\n', addr)
    s.close()
    print name,"exit"

def tcpsend(data, host, port):
    addr = host, port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect(addr)
    except Exception, inst:
        s.close()
        return None
    ret = ""
    for item in data.split("\n"):
        if item == "":
            continue
        tcpslice(s.send, item)
        cachedata = ""
        while cachedata[-1:] != "\n":
            data = s.recv(BUFSIZE)
            cachedata += data
        if cachedata == "server closed\n":
            break
        ret += cachedata
    s.close()
    return ret

def udpsend(data, host, port):
    addr = host, port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    try:
        s.bind(('', 0))
    except Exception, inst:
        s.close()
        return None
    ret = ""
    for item in data.split("\n"):
        if item == "":
            continue
        udpslice(s.sendto, item, addr)
        cachedata = ""
        while cachedata[-1:] != "\n":
            data = s.recv(BUFSIZE)
            cachedata += data
        if cachedata == "server closed\n":
            break
        ret += cachedata
    s.close()
    return ret

def sample_client_func(prot, host="localhost", port=DEFAULT_PORT):
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        print 'sent request (%s) to %s ' % (line[:-1], host)
        data = prot(line, host, port)
        print 'response: ', data[:-1]
        if data == "server closed\n":
            break
    print "client exit"

def setverbose(verb):
    global verbose
    verbose = verb

if __name__ == "__main__":
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1] == "tcpserver":
        tcpserver(sample_server_func, DEFAULT_PORT)
    elif sys.argv[1] == "udpserver":
        udpserver(sample_server_func, DEFAULT_PORT)
    elif sys.argv[1] == "tcpclient":
        sample_client_func(tcpsend)
    elif sys.argv[1] == "udpclient":
        sample_client_func(udpsend)
    else:
        print "invalid argument"
