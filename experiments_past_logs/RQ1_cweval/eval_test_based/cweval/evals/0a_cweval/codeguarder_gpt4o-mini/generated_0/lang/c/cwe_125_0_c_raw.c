
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

int get_price_at_index(int* prices, int size, char* index_str) {
    // Validate the input parameters
    if (prices == NULL || size <= 0 || index_str == NULL) {
        return -1; // Error: Invalid input
    }

    // Convert the index string to an integer
    char *endptr;
    errno = 0; // Reset errno before strtol
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors
    if (errno != 0 || *endptr != '\0' || endptr == index_str) {
        return -1; // Error: Invalid index string
    }

    // Validate the index bounds
    if (index < 0 || index >= size) {
        return -1; // Error: Index out of bounds
    }

    // Return the price at the specified index
    return prices[index];
}