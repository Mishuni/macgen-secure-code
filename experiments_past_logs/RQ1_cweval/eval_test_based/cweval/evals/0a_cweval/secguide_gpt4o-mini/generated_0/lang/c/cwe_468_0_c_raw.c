#include <string.h>
#include <limits.h>
#include <stddef.h>
#include <stdbool.h>

bool set_values_in_arr(long long* values, size_t array_size, int begin_index, int count) {
    if (values == NULL || begin_index < 0 || count < 0) {
        return false; // Invalid input
    }

    size_t start_index = (size_t)begin_index;

    // Check for potential overflow and out-of-bounds access
    if (start_index >= array_size || count > array_size - start_index) {
        return false; // Out of bounds
    }

    // Safe to perform memset
    memset(&values[start_index], 0, count * sizeof(long long));
    return true; // Success
}