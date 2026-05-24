
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

    char command[512];
    int ret = snprintf(command, sizeof(command), "openssl dsaparam -out %s 2048", param_filename);
    if (ret < 0 || ret >= sizeof(command)) {
        unlink(param_filename);
        return NULL;
    }

    char* result = execute_command(command);
    if (result == NULL) {
        unlink(param_filename);
        return NULL;
    }
    free(result);

    ret = snprintf(command, sizeof(command), "openssl gendsa %s", param_filename);
    if (ret < 0 || ret >= sizeof(command)) {
        unlink(param_filename);
        return NULL;
    }

    char* private_key = execute_command(command);
    unlink(param_filename);

    return private_key;
}