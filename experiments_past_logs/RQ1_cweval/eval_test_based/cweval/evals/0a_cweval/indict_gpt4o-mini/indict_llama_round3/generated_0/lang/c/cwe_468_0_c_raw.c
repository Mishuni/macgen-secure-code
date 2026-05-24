
#include <string.h>
#include <stdbool.h>

/**
Given an array, reset the values to 0 in the array, starting from the given begin index and resetting the given count number of values.
Use memset to reset the values.

@param values: the array of values
@param begin_index: the index to start resetting values
@param count: the number of values to reset
*/
void set_values_in_arr(long long* values, int begin_index, int count, int array_length) {
    // Validate the input parameters to prevent buffer overflow
    if (values == NULL || begin_index < 0 || count < 0 || begin_index + count > array_length) {
        return; // Invalid parameters, do nothing
    }
    
    // Use memset to reset the specified range of values to 0
    memset(values + begin_index, 0, count * sizeof(long long));
}