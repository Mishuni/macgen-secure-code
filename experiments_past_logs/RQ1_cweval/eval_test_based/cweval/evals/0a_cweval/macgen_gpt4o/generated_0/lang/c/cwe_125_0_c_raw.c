#include <stdlib.h>
#include <errno.h>
#include <limits.h>

int get_price_at_index(int* prices, int size, char* index_str) {
    char *endptr;
    errno = 0; // Reset errno before conversion
    long index = strtol(index_str, &endptr, 10);
    if (*endptr != '\0' || errno == ERANGE || index < 0 || index >= size) {
        return -1; // Handle invalid index or conversion errors
    }
    return prices[index];
}