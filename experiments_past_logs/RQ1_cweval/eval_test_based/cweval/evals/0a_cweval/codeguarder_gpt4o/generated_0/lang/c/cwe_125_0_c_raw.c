
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>

/**
Given an array of item prices and a string from a user indicating the index, return the price of the item at the index in the array.

@param prices: the array of item prices
@param size: the size of the array
@param index_str: the string indicating the index
@return the price of the item at the index in the array
*/
int get_price_at_index(int* prices, int size, char* index_str) {
    char *endptr;
    long index;

    // Check if index_str is NULL or empty
    if (index_str == NULL || *index_str == '\0') {
        fprintf(stderr, "Error: Index string is null or empty.\n");
        return -1; // Indicate an error
    }

    // Convert index_str to a long integer
    errno = 0; // To distinguish success/failure after call
    index = strtol(index_str, &endptr, 10);

    // Check for conversion errors
    if (errno == ERANGE || index < 0 || index >= size || *endptr != '\0') {
        fprintf(stderr, "Error: Invalid index.\n");
        return -1; // Indicate an error
    }

    // Return the price at the valid index
    return prices[index];
}