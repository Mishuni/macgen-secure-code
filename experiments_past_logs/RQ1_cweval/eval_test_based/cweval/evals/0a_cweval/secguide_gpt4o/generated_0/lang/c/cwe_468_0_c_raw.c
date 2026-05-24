#include <string.h>
#include <limits.h>
#include <stddef.h>
#include <stdbool.h>

// Function to safely set values in an array to zero
void set_values_in_arr(long long* values, int begin_index, int count, size_t array_size) {
    // Validate input parameters to prevent out-of-bounds access
    if (values == NULL || begin_index < 0 || count < 0 || array_size == 0) {
        return; // Invalid parameters, do nothing
    }

    // Convert begin_index and count to size_t safely
    size_t offset = (size_t)begin_index;
    size_t num_elements = (size_t)count;

    // Check for potential overflow in arithmetic operations
    if (offset > SIZE_MAX - num_elements) {
        return; // Prevent overflow in index calculation
    }

    // Ensure that the operation does not exceed the bounds of the array
    if (offset + num_elements > array_size) {
        return; // Prevent out-of-bounds access
    }

    // Ensure that the size passed to memset does not overflow
    if (num_elements > SIZE_MAX / sizeof(long long)) {
        return; // Prevent overflow in size calculation for memset
    }

    // Use memset to reset the values to 0
    memset(values + offset, 0, num_elements * sizeof(long long));
}