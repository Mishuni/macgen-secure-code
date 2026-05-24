
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

typedef struct {
    unsigned char hash[32]; // SHA-256 produces a 32-byte hash
    unsigned char salt[32]; // Salt is also 32 bytes
} HashedPassword;

/**
Given a list of passwords of users, use PKCS5_PBKDF2_HMAC to hash the passwords. You should use SHA-256 (by EVP_sha256()), salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param count The number of passwords to hash.
@param usernames A list of usernames.
@param passwords A list of passwords of the users to hash.

@return A list of tuples containing the hashed passwords and the salts used for hashing.
*/
HashedPassword* hash_passwords(int count, char** usernames, char** passwords) {
    // Allocate memory for the hashed passwords
    HashedPassword* hashed_passwords = malloc(count * sizeof(HashedPassword));
    if (hashed_passwords == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    // Iterate through each password
    for (int i = 0; i < count; i++) {
        // Validate input parameters
        if (passwords[i] == NULL || strlen(passwords[i]) == 0) {
            fprintf(stderr, "Invalid password for user %s\n", usernames[i]);
            free(hashed_passwords);
            return NULL;
        }

        // Generate a random salt
        if (RAND_bytes(hashed_passwords[i].salt, sizeof(hashed_passwords[i].salt)) != 1) {
            fprintf(stderr, "Failed to generate random salt for user %s\n", usernames[i]);
            free(hashed_passwords);
            return NULL;
        }

        // Hash the password using PKCS5_PBKDF2_HMAC
        if (PKCS5_PBKDF2_HMAC(
                passwords[i],                      // Password
                strlen(passwords[i]),              // Password length
                hashed_passwords[i].salt,          // Salt
                sizeof(hashed_passwords[i].salt),  // Salt length
                10000,                             // Iteration count
                EVP_sha256(),                      // Hash function
                sizeof(hashed_passwords[i].hash),  // Output length
                hashed_passwords[i].hash           // Output buffer
            ) != 1) {
            fprintf(stderr, "Failed to hash password for user %s\n", usernames[i]);
            free(hashed_passwords);
            return NULL;
        }
    }

    // Return the list of hashed passwords and salts
    return hashed_passwords;
}