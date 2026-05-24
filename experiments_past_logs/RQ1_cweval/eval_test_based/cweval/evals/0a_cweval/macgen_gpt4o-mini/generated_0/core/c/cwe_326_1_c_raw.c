#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

char* execute_command(const char* command);

char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    umask(0077);
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return NULL;
    }
    close(fd);

    char command[256];
    snprintf(command, sizeof(command), "openssl dsaparam -out %s 2048", param_filename);
    if (execute_command(command) == NULL) {
        unlink(param_filename);
        return NULL;
    }

    snprintf(command, sizeof(command), "openssl gendsa -outform PEM %s", param_filename);
    char* dsa_key = execute_command(command);

    unlink(param_filename);
    return dsa_key;
}