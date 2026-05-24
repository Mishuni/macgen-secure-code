#include <string.h>

void trim_spaces(char* str) {
    if (str == NULL) return;

    size_t len = strlen(str);
    if (len == 0) return;

    size_t i = len;
    while (i > 0 && str[i - 1] == ' ') {
        i--;
    }

    str[i] = '\0';
}