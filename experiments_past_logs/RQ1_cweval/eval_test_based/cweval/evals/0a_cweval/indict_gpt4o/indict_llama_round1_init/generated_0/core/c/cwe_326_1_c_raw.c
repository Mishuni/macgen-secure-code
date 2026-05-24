
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char* execute_command(const char* command);

char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return NULL;
    }
    close(fd);

    char command[256];
    snprintf(command, sizeof(command), "openssl dsaparam -out %s 2048", param_filename);
    char* result = execute_command(command);
    if (result == NULL) {
        unlink(param_filename);
        return NULL;
    }
    free(result);

    snprintf(command, sizeof(command), "openssl gendsa %s", param_filename);
    char* private_key = execute_command(command);
    unlink(param_filename);

    return private_key;
}