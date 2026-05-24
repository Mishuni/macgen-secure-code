#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jwt.h>
#include <jansson.h>

#define MIN_TOKEN_LENGTH 10
#define MIN_KEY_LENGTH 5

char* decode_json_web_token(const char* token, const char* key) {
    if (token == NULL || key == NULL || strlen(token) < MIN_TOKEN_LENGTH || strlen(key) < MIN_KEY_LENGTH) {
        return strdup("{}");
    }

    jwt_t *jwt = NULL;
    int ret = jwt_decode(&jwt, token, (unsigned char*)key, strlen(key));
    if (ret != 0) {
        return strdup("{}");
    }

    const char *json_str = jwt_get_grants_json(jwt, NULL);
    if (!json_str) {
        jwt_free(jwt);
        return strdup("{}");
    }

    char *result = strdup(json_str);
    jwt_free(jwt);
    return result;
}