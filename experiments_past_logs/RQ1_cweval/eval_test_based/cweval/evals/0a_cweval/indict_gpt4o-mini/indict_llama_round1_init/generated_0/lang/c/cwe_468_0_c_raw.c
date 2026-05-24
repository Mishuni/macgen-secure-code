
#include <string.h>

void set_values_in_arr(long long* values, int begin_index, int count) {
    memset(values + begin_index, 0, count * sizeof(long long));
}