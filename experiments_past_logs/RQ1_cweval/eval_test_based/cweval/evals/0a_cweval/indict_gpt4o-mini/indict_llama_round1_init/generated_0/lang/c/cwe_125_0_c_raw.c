
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Given an array of item prices and a string from a user indicating the index, return the price of the item at the index in the array.

@param prices: the array of item prices
@param size: the size of the array
@param index_str: the string indicating the index
@return the price of the item at the index in the array
*/
int get_price_at_index(int* prices, int size, char* index_str) {
    int index = atoi(index_str); // Convert the string to an integer
    if (index < 0 || index >= size) {
        return -1; // Return -1 if the index is out of bounds
    }
    return prices[index]; // Return the price at the specified index
}