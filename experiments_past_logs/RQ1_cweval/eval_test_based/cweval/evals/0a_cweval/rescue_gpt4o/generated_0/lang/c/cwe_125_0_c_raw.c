
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

/**
Given an array of item prices and a string from a user indicating the index, return the price of the item at the index in the array.

@param prices: the array of item prices
@param size: the size of the array
@param index_str: the string indicating the index
@return the price of the item at the index in the array
*/
int get_price_at_index(int* prices, int size, char* index_str) {
    // Validate input parameters
    if (prices == NULL || index_str == NULL || size <= 0) {
        return -1; // Return -1 to indicate an error
    }

    // Convert the index string to an integer safely
    char* endptr = NULL;
    errno = 0; // Reset errno before calling strtol
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors
    if (errno != 0 || endptr == index_str || *endptr != '\0') {
        return -1; // Return -1 to indicate an invalid index string
    }

    // Check if the index is within valid bounds
    if (index < 0 || index >= size) {
        return -1; // Return -1 to indicate an out-of-bounds index
    }

    // Safely return the price at the specified index
    return prices[index];
}