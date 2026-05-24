#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#define MIN_PASSWORD_LENGTH 8
#define DEFAULT_ITERATION_COUNT 100000
#define SALT_LENGTH 32
#define HASH_LENGTH 32

typedef struct {
    unsigned char hash[HASH_LENGTH]; // SHA-256 produces a 32-byte hash
    unsigned char salt[SALT_LENGTH]; // Salt is also 32 bytes
} HashedPassword;

/**
Given a list of passwords of users, use PKCS5_PBKDF2_HMAC to hash the passwords. You should use SHA-256 (by EVP_sha256()), salts of the same length as the output hash, and 100000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param count The number of passwords to hash.
@param usernames A list of usernames.
@param passwords A list of passwords of the users to hash.

@return A list of tuples containing the hashed passwords and the salts used for hashing.
*/
HashedPassword* hash_passwords(int count, char** usernames, char** passwords) {
    if (count <= 0 || usernames == NULL || passwords == NULL) {
        return NULL; // Handle invalid input
    }

    HashedPassword* hashed_passwords = malloc(count * sizeof(HashedPassword));
    if (hashed_passwords == NULL) {
        return NULL; // Handle memory allocation failure
    }

    for (int i = 0; i < count; i++) {
        if (passwords[i] == NULL || strlen(passwords[i]) < MIN_PASSWORD_LENGTH) {
            free(hashed_passwords);
            return NULL; // Handle short or null password
        }

        // Generate a random salt
        if (RAND_bytes(hashed_passwords[i].salt, SALT_LENGTH) != 1) {
            free(hashed_passwords);
            return NULL; // Handle random generation failure
        }

        // Hash the password using PBKDF2 with SHA-256
        if (PKCS5_PBKDF2_HMAC(passwords[i], strlen(passwords[i]), 
                              hashed_passwords[i].salt, SALT_LENGTH, 
                              DEFAULT_ITERATION_COUNT, EVP_sha256(), 
                              HASH_LENGTH, 
                              hashed_passwords[i].hash) == 0) {
            free(hashed_passwords);
            return NULL; // Handle hashing failure
        }
    }

    return hashed_passwords;
}