#include <stdio.h>
#include <stdlib.h>

char *create_private_key() {
    FILE *fp;
    char *key = NULL;
    size_t key_size = 0;
    const char *command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 2>/dev/null";

    fp = popen(command, "r");
    if (fp == NULL) {
        return NULL;
    }

    fseek(fp, 0, SEEK_END);
    key_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    key = (char *)malloc(key_size + 1);
    if (key == NULL) {
        pclose(fp);
        return NULL;
    }

    if (fread(key, 1, key_size, fp) != key_size) {
        free(key);
        pclose(fp);
        return NULL;
    }
    key[key_size] = '\0';

    pclose(fp);
    return key;
}