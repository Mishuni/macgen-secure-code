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
