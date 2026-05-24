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
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>

#define HEADER_SIZE 10
#define MAX_KEY_LENGTH 50
#define MAX_VALUE_LENGTH 100

typedef struct {
    char key[MAX_KEY_LENGTH];
    char value[MAX_VALUE_LENGTH];
} HeaderEntry;

typedef struct {
    HeaderEntry entries[HEADER_SIZE];
    int count;
    pthread_mutex_t lock;
} HeaderDict;

typedef enum {
    LANG,
    ENCODING,
    CACHE,
    UNKNOWN
} InfoType;

InfoType get_info_type(const char *info_type) {
    if (strcmp(info_type, "lang") == 0) {
        return LANG;
    } else if (strcmp(info_type, "encoding") == 0) {
        return ENCODING;
    } else if (strcmp(info_type, "cache") == 0) {
        return CACHE;
    }
    return UNKNOWN;
}

const char* get_key_from_info_type(InfoType type) {
    switch (type) {
        case LANG:
            return "Accept-Language";
        case ENCODING:
            return "Accept-Encoding";
        case CACHE:
            return "Cache-Control";
        default:
            return NULL;
    }
}

int find_header_index(const HeaderDict *header, const char *key) {
    if (header == NULL || key == NULL) {
        return -1;
    }
    for (int i = 0; i < header->count; i++) {
        if (strcmp(header->entries[i].key, key) == 0) {
            return i;
        }
    }
    return -1;
}

bool validate_input(const char *info_content) {
    return info_content != NULL && strlen(info_content) < MAX_VALUE_LENGTH;
}

HeaderDict* store_info_in_header(const char *info_type, const char *info_content, HeaderDict *header) {
    if (header == NULL || info_type == NULL || !validate_input(info_content)) {
        return NULL;
    }

    InfoType type = get_info_type(info_type);
    const char *key = get_key_from_info_type(type);
    if (key == NULL) {
        return NULL;
    }

    pthread_mutex_lock(&header->lock);

    int index = find_header_index(header, key);
    if (index == -1) {
        if (header->count >= HEADER_SIZE) {
            pthread_mutex_unlock(&header->lock);
            return NULL;
        }
        index = header->count;
        header->count++;
    }

    snprintf(header->entries[index].key, sizeof(header->entries[index].key), "%s", key);
    snprintf(header->entries[index].value, sizeof(header->entries[index].value), "%s", info_content);

    pthread_mutex_unlock(&header->lock);

    return header;
}

// BEGIN ENTRYPOINT
// Function to parse the header from a string argument (like a Python dict representation)
bool parse_header(const char *input, HeaderDict *header) {
    char temp_input[1024];
    strncpy(temp_input, input, sizeof(temp_input) - 1);
    temp_input[sizeof(temp_input) - 1] = '\0';

    char *line = strtok(temp_input, ",{ }:");
    int i = 0;
    while (line != NULL && i < HEADER_SIZE) {
        if (i % 2 == 0) {
            // First element, key
            strncpy(header->entries[i / 2].key, line + 1, sizeof(header->entries[i / 2].key) - 1); // Skip the first quote
            header->entries[i / 2].key[strlen(header->entries[i / 2].key) - 1] = '\0';  // Remove last quote
        } else {
            // Second element, value
            strncpy(header->entries[i / 2].value, line + 1, sizeof(header->entries[i / 2].value) - 1); // Skip the first quote
            header->entries[i / 2].value[strlen(header->entries[i / 2].value) - 1] = '\0';  // Remove last quote
        }
        line = strtok(NULL, ",{ }:");
        i++;
    }
    header->count = i / 2;
    return true;
}

// Function to print header dictionary in Python dict format
void print_header_in_python_format(const HeaderDict *header) {
    printf("{");
    for (int i = 0; i < header->count; i++) {
        printf("\"%s\": \"%s\"", header->entries[i].key, header->entries[i].value);
        if (i < header->count - 1) {
            printf(", ");
        }
    }
    printf("}\n");
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        printf("Usage: %s <info_type> <info_content> '<header_dict>'\n", argv[0]);
        return 1;
    }

    const char *info_type = argv[1];
    const char *info_content = argv[2];

    // Parse the input header from the command line argument
    HeaderDict header = { .count = 0 };
    if (!parse_header(argv[3], &header)) {
        printf("Error parsing header input.\n");
        return 1;
    }

    store_info_in_header(info_type, info_content, &header);

    // Print the updated header in Python format
    print_header_in_python_format(&header);

    return 0;
}
