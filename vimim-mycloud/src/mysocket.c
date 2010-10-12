/*
    socket function for both WinSock and Linux 
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
 */

#ifdef WIN32
# include <winsock2.h>
# include <wininet.h>
#else
# include <sys/types.h>          /* See NOTES */
# include <sys/socket.h>
# include <arpa/inet.h>
# include <unistd.h>
#endif

#include <stdio.h>
#include <string.h>
#include "mycloud.h"

int tcpsend(char *ret, const char *src, const char *host, unsigned short port)
{
#ifdef WIN32
    /* init winsock */
    WSADATA       wsd;
    if (WSAStartup(MAKEWORD(2,2), &wsd) != 0) {
        printf("Failed to load Winsock library!\n");
        goto error0;
    }
#endif

    /* limit the data length */
    int lensrc = strlen(src);
    if (lensrc >= BUFSIZ)
        goto error1;
    /* create the socket */
#ifdef WIN32
    SOCKET s = socket(AF_INET, SOCK_STREAM, 0);
#else
    int s = socket(PF_INET, SOCK_STREAM, 0);
#endif
    if (s < 0) 
        goto error1;
    /* assign the address */
    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof serv_addr);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(host);
    serv_addr.sin_port = htons(port);

    if (connect(s, (struct sockaddr *)&serv_addr, sizeof serv_addr) < 0)
        goto error2;

    if (src[lensrc-1] == '\n') {
        lensrc--;
    }
    if (send(s, src, lensrc, 0) != lensrc)
        goto error2;
    send(s, "\n", 1, 0);
    ret[0] = '\0';
    for (int i=OUTPUT_BUFFERS; ;i--) {
        char buf[BUFSIZ];
        size_t sz = recv(s, buf, sizeof buf - 1, 0);
        if (sz <= 0)
            goto error2;
        buf[sz] = '\0';
        if (i > 0)
            strcat(ret, buf);
        else {
            size_t len = strlen(ret);
            ret[len-2] = '\n';
            ret[len-1] = '\0';
        }
        if (buf[sz-1] == '\n')
            break;
    }
#ifdef WIN32
    closesocket(s);
#else
    close(s);
#endif
    return 0;

error2:
#ifdef WIN32
    closesocket(s);
#else
    close(s);
#endif
error1:
#ifdef WIN32
    WSACleanup();
error0:
#endif
    ret[0] = '\0';
    return 0;
}

#ifdef WIN32
int win32_geturl(char *ret, const char *url)
{
    HINTERNET hInet = InternetOpen(NULL,INTERNET_OPEN_TYPE_PRECONFIG,NULL,NULL,0);
    if (hInet == NULL)
        goto myerror0;

    HINTERNET hUrl = InternetOpenUrl(hInet,url,NULL,0,0,0);
    if (hUrl == NULL)
        goto myerror1;
    ret[0] = '\0';
    for (int i = OUTPUT_BUFFERS; ;i-- ) {
        char buf[BUFSIZ];
        DWORD len;
        BOOL b = InternetReadFile(hUrl, buf, sizeof buf - 1, &len);
        if (b == FALSE)
            goto myerror2;
        if (len == 0)
            break;
        buf[len] = '\0';
        if (i > 0)
            strcat(ret, buf);
    }

    InternetCloseHandle(hUrl);
    InternetCloseHandle(hInet);
    return 0;

myerror2:
    InternetCloseHandle(hUrl);
myerror1:
    InternetCloseHandle(hInet);
myerror0:
    ret[0] = '\0';
    return 1;
}
#endif
