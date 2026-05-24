#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void set_values_in_arr(long long* values, int begin_index, int count) {
    const int array_size = 15;

    if (values == NULL || begin_index < 0 || begin_index >= array_size) {
        return;
    }

    if (count < 0) {
        return;
    }

    int effective_count = (begin_index + count > array_size) ? (array_size - begin_index) : count;

    if (effective_count > 0) {
        memset(&values[begin_index], 0, effective_count * sizeof(long long));
    }
}