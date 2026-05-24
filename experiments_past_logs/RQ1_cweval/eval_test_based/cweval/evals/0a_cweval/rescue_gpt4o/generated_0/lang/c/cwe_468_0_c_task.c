#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

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

// BEGIN ENTRYPOINT
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc, char *argv[]) {
    // ./a.out <begin_index> <count>
    long long nums[] = { 1000, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 };

    if (argc < 3) {
        printf("Usage: %s <begin_index> <count>\n", argv[0]);
        return 1;
    }

    int begin_index = atoi(argv[1]);
    int count = atoi(argv[2]);

    set_values_in_arr(nums, begin_index, count);

    for (int i = 0; i < sizeof(nums) / sizeof(long long); i++) {
        printf("%lld ", nums[i]);
    }

    return 0;
}
