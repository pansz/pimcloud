#include <stdio.h>
#include <string.h>
#include "mycloud.h"
#include <stdlib.h>

int main(int argc, char *argv[])
{
    char *ret;
    char str1[BUFSIZ]=
        "ime_query_res=\"%E4%BD%A0%E4%BB%AC%E5%A5%BD%EF%BC%9A8%09+%E4%BD%A0%E4%BB%AC%EF%BC%9A5%09+%E4%BD%A0%E9%97%B7%EF%BC%9A5%09+%E5%80%AA%E6%89%AA%EF%BC%9A5%09+%E6%B3%A5%E6%89%AA%EF%BC%9A5%09+%E6%8B%9F%E6%89%AA%EF%BC%9A5%09+";
    char str2[BUFSIZ] ="%E4%BD%A0%EF%BC%9A2%09+%E6%8B%9F%EF%BC%9A2%09+%E5%91%A2%EF%BC%9A2%09+%E5%B0%BC%EF%BC%9A2%09+%E6%B3%A5%EF%BC%9A2%09+%E9%80%86%EF%BC%9A2%09+%E5%A6%AE%EF%BC%9A2%09+%E8%85%BB%EF%BC%9A2%09+%E5%80%AA%EF%BC%9A2%09+%E4%BC%B1%EF%BC%9A2%09+%E5%8C%BF%EF%BC%9A2%09+%E6%BA%BA%EF%BC%9A2%09+%E9%9C%93%EF%BC%9A2%09+%E5%84%9E%EF%BC%9A2\";"
        "ime_query_key=\"nimenhao\";";
    strcat(str1, str2);
    ret = do_unquote(str1);
    printf("do_unquote: %s\n", ret);

    base64_decode(str1, "X19nZXRrZXljaGFycw==");
    printf("base64_decode: %s\n", str1);
    base64_encode(str1, "__getkeychars");
    printf("base64_encode: %s\n", str1);
    int result = strcmp(str1, "X19nZXRrZXljaGFycw==");
    printf("strcmp result: %d\n", result);

    ret = do_getlocal("172.16.55.26 __isvalid");
    printf("do_getlocal: %s\n", ret);
    ret = do_getlocal("172.16.55.26 nimfhk");
    printf("do_getlocal: %s\n", ret);

    ret = do_geturl("__isvalid");
    printf("do_geturl: %s\n", ret);
    ret = do_geturl("http://web.pinyin.sogou.com/web_ime/get_ajax/nimenhao.key");
    printf("do_geturl: %s\n", ret);
    ret = do_unquote(ret);
    printf("do_unquote: %s\n", ret);

#ifdef WIN32
    exit(0);
#else
    return 0;
#endif
}

