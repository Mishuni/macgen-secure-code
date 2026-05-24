#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <errno.h>

#define ERROR_INVALID_INPUT -1
#define ERROR_INVALID_INDEX -2

int get_price_at_index(int* prices, int size, char* index_str) {
    // Ensure the prices pointer is not NULL and size is non-negative
    if (prices == NULL || index_str == NULL || size < 0) {
        return ERROR_INVALID_INPUT; // Return an error code for invalid input
    }

    // Convert the index string to an integer
    char* endptr;
    errno = 0; // Reset errno before calling strtol
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors and range issues
    if (errno != 0 || *endptr != '\0' || index < 0 || index >= size || index > INT_MAX) {
        return ERROR_INVALID_INDEX; // Return an error code for invalid index
    }

    // Return the price at the specified index
    return prices[(int)index];
}