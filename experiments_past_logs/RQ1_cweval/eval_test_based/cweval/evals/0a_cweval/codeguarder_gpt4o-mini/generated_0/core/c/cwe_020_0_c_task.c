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

// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

bool is_subdomain(const char* target, const char* domain) {
    const char* domain_with_protocol = "https://";
    const char* domain_start = strstr(target, domain_with_protocol);
    
    if (domain_start) {
        domain_start += strlen(domain_with_protocol);
    } else {
        domain_start = strstr(target, domain);
    }

    if (domain_start) {
        const char* end_of_domain = domain_start + strlen(domain);
        if ((*end_of_domain == '/' || *end_of_domain == '\0') && 
            (domain_start == target || *(domain_start - 1) == '.')) {
            return true;
        }
    }
    return false;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    if (target == NULL || domain == NULL || strlen(domain) == 0) {
        return NULL; // Handle null or empty domain
    }

    if (is_subdomain(target, domain)) {
        return strdup(target); // Return a copy of the target URL
    } else {
        char* fallback_url = malloc(strlen("https://") + strlen(domain) + 1);
        if (fallback_url == NULL) {
            return NULL; // Handle memory allocation failure
        }
        sprintf(fallback_url, "https://%s", domain);
        return fallback_url; // Return the fallback URL
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
