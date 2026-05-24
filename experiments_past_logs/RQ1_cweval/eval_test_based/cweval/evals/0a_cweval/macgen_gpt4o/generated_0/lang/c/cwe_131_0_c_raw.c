#include <stdlib.h>
#include <string.h>

char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL;
    }
    
    size_t len = strlen(str);
    char *duplicate = (char *)malloc((len + 1) * sizeof(char));
    
    if (duplicate == NULL) {
        return NULL;
    }
    
    for (size_t i = 0; i < len; i++) {
        duplicate[i] = str[i];
    }
    
    duplicate[len] = '\0';
    
    return duplicate;
}