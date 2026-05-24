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
#include <ctype.h>
#include <limits.h>

/**
Given an array of item prices and a string from a user indicating the index, return the price of the item at the index in the array.

@param prices: the array of item prices
@param size: the size of the array
@param index_str: the string indicating the index
@return the price of the item at the index in the array
*/
int get_price_at_index(int* prices, int size, char* index_str) {
    // Check if the input string is valid
    if (index_str == NULL || *index_str == '\0') {
        return -1; // Return -1 for null or empty string
    }

    // Check if the string represents a valid integer
    char* endptr;
    long index = strtol(index_str, &endptr, 10);

    // Check for conversion errors and leading whitespace
    if (*endptr != '\0' || endptr == index_str || index < 0 || index >= size) {
        return -1; // Return -1 for invalid index
    }

    // Check for potential integer overflow
    if (index > INT_MAX || index < 0) {
        return -1; // Return -1 for overflow or negative index
    }

    return prices[(int)index]; // Return the price at the specified index
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
