
#include <jwt.h>
#include <string.h>
#include <jansson.h>

char* decode_json_web_token(const char* token, const char* key) {
    jwt_t *jwt = NULL;
    const char *claims_json = "{}"; // Default to empty JSON object string
    char *decoded_claims = NULL;

    if (jwt_decode(&jwt, token, (unsigned char*)key, strlen(key)) == 0) {
        json_t *claims = jwt_get_grants_json(jwt, NULL);
        if (claims) {
            decoded_claims = json_dumps(claims, 0);
            json_decref(claims);
        }
        jwt_free(jwt);
    }

    return decoded_claims ? decoded_claims : strdup(claims_json);
}