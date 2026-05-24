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
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

int print_rand_num_plus_offset(int offset) {
    if (offset < 0) {
        fprintf(stderr, "Offset must be non-negative.\n");
        return -1; // Error: invalid offset
    }

    // Seed the random number generator once
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned int)time(NULL));
        seeded = 1;
    }

    // Generate a positive random number
    int rand_num = rand(); // rand() returns a number in [0, RAND_MAX]

    // Check for potential overflow before performing the addition
    if (offset > INT_MAX - rand_num) {
        fprintf(stderr, "Overflow would occur when adding offset.\n");
        return -1; // Error: overflow
    }

    // Calculate the result with offset
    long long result = (long long)rand_num + (long long)offset;

    // Check for overflow before printing
    if (result > INT_MAX || result < INT_MIN) {
        fprintf(stderr, "Overflow occurred when calculating result.\n");
        return -1; // Error: overflow
    }

    // Print the result as an int
    printf("%d\n", (int)result);
    return 0; // Success
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // ./a.out offset
    if (argc != 2) {
        printf("Usage: %s offset\n", argv[0]);
        return 1;
    }
    int offset = atoi(argv[1]);
    print_rand_num_plus_offset(offset);
    return 0;
}
