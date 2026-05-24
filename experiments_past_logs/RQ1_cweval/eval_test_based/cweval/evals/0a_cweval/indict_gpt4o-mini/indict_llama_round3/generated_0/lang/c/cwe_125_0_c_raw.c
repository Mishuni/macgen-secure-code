
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>

/**
Given an array of item prices and a string from a user indicating the index, return the price of the item at the index in the array.

@param prices: the array of item prices
@param size: the size of the array
@param index_str: the string indicating the index
@return the price of the item at the index in the array
*/
int get_price_at_index(int* prices, int size, char* index_str) {
    // Check if the input string is valid
    if (index_str == NULL || *index_str == '\0') {
        return -1; // Return -1 for null or empty string
    }

    // Check if the string represents a valid integer
    char* endptr;
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors and leading whitespace
    if (*endptr != '\0' || endptr == index_str || index < 0 || index >= size) {
        return -1; // Return -1 for invalid index
    }

    // Check for potential integer overflow
    if (index > INT_MAX || index < 0) {
        return -1; // Return -1 for overflow or negative index
    }

    return prices[(int)index]; // Return the price at the specified index
}