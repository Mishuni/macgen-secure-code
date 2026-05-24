
#include <string.h>

void trim_spaces(char* str) {
    int length = strlen(str);
    if (length == 0) return;

    int end = length - 1;
    while (end >= 0 && str[end] == ' ') {
        end--;
    }

    str[end + 1] = '\0';
}