
#include <jwt.h>
#include <string.h>
#include <jansson.h>

char* decode_json_web_token(const char* token, const char* key) {
    jwt_t *jwt = NULL;
    const char *claims_json = "{}"; // Default to empty JSON object string
    char *decoded_claims = NULL;

    // Attempt to decode the JWT
    if (jwt_decode(&jwt, token, (unsigned char*)key, strlen(key)) == 0) {
        // Retrieve the claims as a JSON object
        json_t *claims = jwt_get_grants_json(jwt, NULL);
        if (claims) {
            // Convert the JSON object to a string
            decoded_claims = json_dumps(claims, 0);
            json_decref(claims);
        }
        jwt_free(jwt);
    }

    // Return the decoded claims or an empty JSON object string
    if (decoded_claims) {
        return decoded_claims;
    } else {
        return strdup(claims_json);
    }
}