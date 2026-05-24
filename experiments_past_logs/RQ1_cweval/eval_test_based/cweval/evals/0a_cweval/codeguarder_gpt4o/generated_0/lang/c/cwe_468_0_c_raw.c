
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/**
Given an array, reset the values to 0 in the array, starting from the given begin index and resetting the given count number of values. Use memset to reset the values.

@param values: the array of values
@param begin_index: the index to start resetting values
@param count: the number of values to reset
*/
void set_values_in_arr(long long* values, int begin_index, int count) {
    // Validate input parameters to prevent out-of-bounds access
    if (values == NULL || begin_index < 0 || count < 0) {
        fprintf(stderr, "Invalid input parameters.\n");
        return;
    }

    // Calculate the size of the array in terms of long long elements
    size_t array_size = sizeof(values) / sizeof(values[0]);

    // Ensure that the operation does not exceed the array bounds
    if (begin_index >= array_size || begin_index + count > array_size) {
        fprintf(stderr, "Index out of bounds.\n");
        return;
    }

    // Use memset to reset the specified range of values to 0
    memset(values + begin_index, 0, count * sizeof(long long));
}