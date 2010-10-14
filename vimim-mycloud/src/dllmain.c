/*
    plugin for vim libcall()
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

#include <stdio.h>
#include <string.h>
#include "mycloud.h"
#include "cdecode.h"
#include "cencode.h"

char buffer1[OUTPUT_BUFFERS*BUFSIZ];
char buffer2[OUTPUT_BUFFERS*BUFSIZ];

char *do_geturl(const char *url)
{
    char *geturl = buffer2;

#ifndef WIN32
    if (strcmp(url, "__isvalid") == 0) {
        strcpy(geturl, "False");
        return geturl;
    } else {
        geturl[0] = '\0';
        return geturl;
    }
#else
    if (strcmp(url, "__isvalid") == 0) {
        strcpy(geturl, "True");
        return geturl;
    } else {
        win32_geturl(geturl, url);
        return geturl;
    }
#endif
}

/* unquote the %xx url quote */
char *do_unquote(const char *src)
{
    char *unquote = buffer1;
    size_t i;
    const char *p = src;
    for (i = 0; p[0] != '\0'; i++) {
        if (p[0] == '%') {
            unsigned int x = 0x20;
            int ret = sscanf(p+1, "%02X", &x);
            if (ret != 1) {
                unquote[i] = '%';
                p ++;
            } else {
                unquote[i] = x & 0xff;
                p += 3;
            }
        } else {
            unquote[i] = *p;
            p ++;
        }
    }
    unquote[i] = '\0';
    return unquote;
}

int base64_encode(char *to, const char *from)
{
    base64_encodestate state;

    base64_init_encodestate(&state);
    to[0] = '\0';
    int codelength1 = base64_encode_block(from, strlen(from), to, &state);
    int codelength2 = base64_encode_blockend(to+codelength1, &state);
    to[codelength1+codelength2] = '\0';

    return codelength1+codelength2;
}

int base64_decode(char *to, const char *from)
{
    base64_decodestate state;

    base64_init_decodestate(&state);
    to[0] = '\0';

    int plainlength = base64_decode_block(from, strlen(from), to, &state);

    return plainlength;
}

char *do_getlocal(const char *keyb)
{
    char *getlocal = buffer1;
    char *temp = buffer2;
    char host[16];
    strcpy(temp, keyb);
    char *space = strstr(temp, " ");

    if (space == NULL) {
        strcpy(host, "127.0.0.1");
        space = temp;
    } else {
        space[0] = '\0';
        strncpy(host, keyb, 16);
        host[15] = '\0';
        space++;
    }

    base64_encode(getlocal, space);
    tcpsend(temp, getlocal, host, 10007);
    base64_decode(getlocal, temp);

    return getlocal;
}

char *do_test(const char *dummy)
{
    static char result[8];
    static int i = 0;
    i++;
    sprintf(result, "%d", i);
    return result;
}

