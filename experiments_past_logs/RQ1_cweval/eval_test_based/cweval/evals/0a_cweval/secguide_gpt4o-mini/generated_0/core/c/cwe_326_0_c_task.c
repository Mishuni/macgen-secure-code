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
#include <unistd.h>

char *create_private_key() {
    const int key_length = 2048; // You can adjust the key length as needed
    char *command = NULL;
    size_t command_size = 0;
    
    // Dynamically allocate memory for the command string
    command_size = snprintf(NULL, 0, "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d", key_length) + 1;
    command = malloc(command_size);
    if (command == NULL) {
        return NULL; // Memory allocation failed
    }
    snprintf(command, command_size, "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d", key_length);

    FILE *fp = popen(command, "r");
    free(command); // Free command memory after use
    if (fp == NULL) {
        return NULL; // Failed to open process
    }

    char *private_key = NULL;
    size_t key_size = 0;
    ssize_t read;

    // Read the output from the command
    while ((read = getline(&private_key, &key_size, fp)) != -1) {
        // Continue reading until the end of the output
    }

    pclose(fp);

    // Check if the key was generated successfully
    if (private_key == NULL || strlen(private_key) == 0) {
        free(private_key); // Free memory if key generation failed
        return NULL;
    }

    return private_key; // Caller is responsible for freeing the returned key
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
