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
#include <openssl/pem.h>
#include <openssl/rsa.h>

char *create_private_key() {
    const int key_length = 2048; // Desired key length
    RSA *rsa = RSA_generate_key(key_length, RSA_F4, NULL, NULL);
    if (rsa == NULL) {
        return NULL; // Error generating key
    }

    BIO *bio = BIO_new(BIO_s_mem());
    if (bio == NULL) {
        RSA_free(rsa);
        return NULL; // Error creating BIO
    }

    if (PEM_write_bio_RSAPrivateKey(bio, rsa, NULL, NULL, 0, NULL, NULL) != 1) {
        BIO_free(bio);
        RSA_free(rsa);
        return NULL; // Error writing key to BIO
    }

    BUF_MEM *buf;
    BIO_get_mem_ptr(bio, &buf);
    char *private_key = malloc(buf->length + 1);
    if (private_key == NULL) {
        BIO_free(bio);
        RSA_free(rsa);
        return NULL; // Memory allocation failed
    }

    BIO_read(bio, private_key, buf->length);
    private_key[buf->length] = '\0'; // Null-terminate the string

    BIO_free(bio);
    RSA_free(rsa);
    return private_key; // Return the generated RSA private key in PEM format
}

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    char *private_key = create_private_key();
    if (private_key != NULL) {
        printf("%s", private_key);
        free(private_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate private key\n");
    }

    return 0;
}
