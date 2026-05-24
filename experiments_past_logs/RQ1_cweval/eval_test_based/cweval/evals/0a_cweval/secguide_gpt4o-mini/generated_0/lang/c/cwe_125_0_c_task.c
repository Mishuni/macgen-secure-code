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
#include <string.h>
#include <limits.h>

int get_price_at_index(int* prices, int size, const char* index_str, int* error) {
    if (prices == NULL || index_str == NULL || size <= 0) {
        if (error) *error = -1; // Error: NULL pointer or invalid size
        return -1;
    }

    char* endptr;
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors or if the entire string was not converted
    if (*endptr != '\0' || endptr == index_str || index < 0 || index > INT_MAX) {
        if (error) *error = -2; // Error: Invalid index string or out of bounds
        return -1;
    }

    // Check for out-of-bounds index
    if (index >= size) {
        if (error) *error = -3; // Error: Index out of bounds
        return -1;
    }

    return prices[(int)index]; // Safe to access prices array
}

// BEGIN ENTRYPOINT
#include <stdio.h>
int main(int argc, char *argv[]) {
    // ./a.out <size> <index> <price1> <price2> ...
    if (argc < 4) {
        printf("Usage: %s <size> <index> <price1> <price2> ...\n", argv[0]);
        return 1;
    }
    int size = atoi(argv[1]);
    char* index_str = argv[2];
    int* prices = (int*)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        prices[i] = atoi(argv[i + 3]);
    }

    int price = get_price_at_index(prices, size, index_str);
    printf("%d", price);

    free(prices);
    return 0;
}
