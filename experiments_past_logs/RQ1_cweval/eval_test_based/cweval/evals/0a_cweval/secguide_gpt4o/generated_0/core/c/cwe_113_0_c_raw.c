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