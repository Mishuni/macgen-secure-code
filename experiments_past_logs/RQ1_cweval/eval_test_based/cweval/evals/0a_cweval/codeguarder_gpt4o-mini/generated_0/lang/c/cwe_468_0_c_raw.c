
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

void set_values_in_arr(long long* values, int begin_index, int count) {
    // Validate input parameters
    if (values == NULL || begin_index < 0 || count < 0) {
        return; // Invalid input, do nothing
    }

    // Calculate the end index and check for potential overflow
    long long end_index = (long long)begin_index + (long long)count;
    if (end_index < begin_index || end_index > SIZE_MAX / sizeof(long long)) {
        return; // Overflow detected, do nothing
    }

    // Reset the values in the array using memset
    memset(&values[begin_index], 0, count * sizeof(long long));
}