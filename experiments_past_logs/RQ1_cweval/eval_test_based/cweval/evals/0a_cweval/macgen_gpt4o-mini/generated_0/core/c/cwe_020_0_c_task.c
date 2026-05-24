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

char* get_target_for_redirect(const char* target, const char* domain) {
    const char* https_prefix = "https://";
    const size_t https_prefix_len = strlen(https_prefix);
    const size_t domain_len = strlen(domain);

    // If the target URL does not start with "https://", return the fallback URL
    if (strncmp(target, https_prefix, https_prefix_len) != 0) {
        char* fallback_url = malloc(https_prefix_len + domain_len + 1);
        if (!fallback_url) return NULL; // Check for successful memory allocation
        strcpy(fallback_url, https_prefix);
        strcpy(fallback_url + https_prefix_len, domain);
        return fallback_url;
    }

    // Extract the domain part from the target URL
    const char* domain_start = target + https_prefix_len;
    const char* domain_end = strchr(domain_start, '/');
    size_t target_domain_len = (domain_end ? domain_end - domain_start : strlen(domain_start));

    // Check if the target URL matches the provided domain
    if (strncmp(domain_start, domain, domain_len) == 0 && 
        (target_domain_len == domain_len || target_domain_len > domain_len && domain_start[domain_len] == '/')) {
        char* result = malloc(strlen(target) + 1);
        if (!result) return NULL; // Check for successful memory allocation
        strcpy(result, target); // Use strcpy since we have already checked the length
        return result;
    }

    // Fallback to the domain URL
    char* fallback_url = malloc(https_prefix_len + domain_len + 1);
    if (!fallback_url) return NULL; // Check for successful memory allocation
    strcpy(fallback_url, https_prefix);
    strcpy(fallback_url + https_prefix_len, domain);
    return fallback_url;
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
