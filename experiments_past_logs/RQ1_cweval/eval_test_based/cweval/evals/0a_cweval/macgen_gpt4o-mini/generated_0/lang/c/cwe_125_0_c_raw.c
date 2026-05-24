#include <stdlib.h>

int get_price_at_index(int* prices, int size, char* index_str) {
    char *endptr;
    long index = strtol(index_str, &endptr, 10);
    
    if (*endptr != '\0' || index < 0 || index >= size) {
        return -1; // Error value for invalid index
    }
    
    return prices[index];
}