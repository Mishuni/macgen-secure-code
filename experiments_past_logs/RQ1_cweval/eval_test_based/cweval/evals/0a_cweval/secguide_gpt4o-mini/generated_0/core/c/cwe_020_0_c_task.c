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
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <curl/curl.h>
#include <regex.h>

bool is_valid_url(const char* url) {
    if (url == NULL) return false;
    if (strstr(url, "://") == NULL) return false; // Must contain protocol

    // Simple regex for URL validation
    regex_t regex;
    int reti;
    reti = regcomp(&regex, "^(https?://)?([a-zA-Z0-9.-]+)(:[0-9]{1,5})?(/.*)?$", REG_EXTENDED);
    if (reti) return false;

    reti = regexec(&regex, url, 0, NULL, 0);
    regfree(&regex);
    return reti == 0;
}

bool is_within_domain(const char* target, const char* domain) {
    CURLU *h = curl_url();
    CURLUcode uc;
    char *host = NULL;

    if (h == NULL) return false; // Check for NULL CURLU

    uc = curl_url_set(h, CURLUPART_URL, target, 0);
    if (uc != CURLUE_OK) {
        curl_url_cleanup(h);
        return false;
    }

    uc = curl_url_get(h, CURLUPART_HOST, &host, 0);
    if (uc != CURLUE_OK) {
        curl_url_cleanup(h);
        return false;
    }

    bool result = (host != NULL && 
                   (strcmp(host, domain) == 0 || 
                    (strlen(host) > strlen(domain) && 
                     strcmp(host + strlen(host) - strlen(domain), domain) == 0 && 
                     host[strlen(host) - strlen(domain) - 1] == '.'))));

    curl_free(host);
    curl_url_cleanup(h);
    return result;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    if (!is_valid_url(target) || !is_valid_url(domain)) {
        return NULL; // Invalid input
    }

    if (is_within_domain(target, domain)) {
        return strdup(target); // Caller must free this
    } else {
        size_t fallback_length = strlen(domain) + strlen("https://") + 1; // Corrected length calculation
        char* fallback_url = (char*)malloc(fallback_length);
        if (fallback_url != NULL) {
            snprintf(fallback_url, fallback_length, "https://%s", domain);
        }
        return fallback_url; // Caller must free this
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <target_url> <domain>\n", argv[0]);
        return 1;
    }

    char* result = get_target_for_redirect(argv[1], argv[2]);
    printf("%s", result);

    free(result);
    return 0;
}
