#include <stdlib.h>
#include <string.h>
#include <stdint.h>

char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL;
    }
    
    size_t length = strlen(str);
    if (length > SIZE_MAX - 1) { // Check for excessively large strings
        return NULL;
    }
    
    char* duplicate = (char*)malloc(length + 1);
    if (duplicate == NULL) {
        return NULL;
    }
    
    for (size_t i = 0; i < length; i++) {
        duplicate[i] = str[i];
    }
    duplicate[length] = '\0';
    
    return duplicate;
}