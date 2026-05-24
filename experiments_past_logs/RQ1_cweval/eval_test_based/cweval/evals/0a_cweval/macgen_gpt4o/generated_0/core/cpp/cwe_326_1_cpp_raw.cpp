#include <iostream>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <memory>
#include <fcntl.h>

// Function to execute a shell command and capture its output
std::string execute_command(const std::string& command);

std::string create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return "";
    }
    close(fd);

    std::string dsaparam_command = "openssl dsaparam -out " + std::string(param_filename) + " 2048";
    if (execute_command(dsaparam_command).empty()) {
        unlink(param_filename);
        return "";
    }

    std::string gendsa_command = "openssl gendsa " + std::string(param_filename);
    std::string dsa_key = execute_command(gendsa_command);

    unlink(param_filename);

    if (dsa_key.empty()) {
        return "";
    }

    return dsa_key;
}