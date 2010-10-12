#ifndef __MYCLOUD_H
#define __MYCLOUD_H

char *do_geturl(const char *url);
char *do_unquote(const char *src);

int base64_encode(char *to, const char *from);
int base64_decode(char *to, const char *from);
int tcpsend(char *result, const char *data, const char *host, unsigned short port);
int win32_geturl(char *result, const char *url);

char *do_getlocal(const char *keyb);

char *do_test(const char *dummy);

#define OUTPUT_BUFFERS 8

#endif
