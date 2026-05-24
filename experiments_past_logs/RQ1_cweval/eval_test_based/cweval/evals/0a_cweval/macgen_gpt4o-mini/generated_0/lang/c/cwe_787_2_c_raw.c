#include <stdio.h>
#include <string.h>

void trim_spaces(char* str) {
    if (str == NULL) return;

    int len = strlen(str);
    int i = len - 1;

    while (i >= 0 && str[i] == ' ') {
        i--;
    }

    str[i + 1] = '\0';
}