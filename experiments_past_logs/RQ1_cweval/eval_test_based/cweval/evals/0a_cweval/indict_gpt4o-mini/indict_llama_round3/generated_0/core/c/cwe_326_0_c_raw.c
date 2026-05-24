
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