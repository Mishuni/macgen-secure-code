
#include <stdlib.h>
#include <errno.h>
#include <limits.h>

int get_price_at_index(int* prices, int size, char* index_str) {
    if (prices == NULL || index_str == NULL) {
        return -1; // Return -1 if the prices array or index_str is NULL
    }

    char* endptr;
    errno = 0; // Reset errno before calling strtol
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors and ensure index is within bounds
    if (errno != 0 || endptr == index_str || *endptr != '\0' || index < 0 || index >= size) {
        return -1; // Return -1 if conversion failed or index is out of bounds
    }

    return prices[index];
}