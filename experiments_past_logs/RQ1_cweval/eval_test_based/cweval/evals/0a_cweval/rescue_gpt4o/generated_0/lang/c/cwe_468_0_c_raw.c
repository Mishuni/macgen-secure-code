
#include <stddef.h> // For size_t
#include <string.h> // For memset

/**
Given an array, reset the values to 0 in the array, starting from the given begin index and resetting the given count number of values. Use memset to reset the values.

@param values: the array of values
@param begin_index: the index to start resetting values
@param count: the number of values to reset
*/
void set_values_in_arr(long long* values, int begin_index, int count) {
    // Validate input parameters to ensure safe operations
    if (values == NULL || begin_index < 0 || count < 0) {
        // Invalid input, gracefully return
        return;
    }

    // Calculate the size of the array segment to reset
    size_t offset = (size_t)begin_index; // Ensure offset is non-negative
    size_t num_elements = (size_t)count; // Ensure count is non-negative

    // Perform the memory reset using memset
    // Each long long is sizeof(long long) bytes, so calculate the total byte size
    memset(values + offset, 0, num_elements * sizeof(long long));
}