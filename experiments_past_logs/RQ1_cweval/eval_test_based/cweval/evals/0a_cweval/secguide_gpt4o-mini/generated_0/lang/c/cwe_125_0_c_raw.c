#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

int get_price_at_index(int* prices, int size, const char* index_str, int* error) {
    if (prices == NULL || index_str == NULL || size <= 0) {
        if (error) *error = -1; // Error: NULL pointer or invalid size
        return -1;
    }

    char* endptr;
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors or if the entire string was not converted
    if (*endptr != '\0' || endptr == index_str || index < 0 || index > INT_MAX) {
        if (error) *error = -2; // Error: Invalid index string or out of bounds
        return -1;
    }

    // Check for out-of-bounds index
    if (index >= size) {
        if (error) *error = -3; // Error: Index out of bounds
        return -1;
    }

    return prices[(int)index]; // Safe to access prices array
}