#include <iostream>
#include <string>
#include <memory>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <sys/stat.h>

std::string execute_command(const std::string& command);

std::string create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return "";
    }
    close(fd);

    const int key_length = 2048; // Desired key length
    std::string param_command = "openssl dsaparam -out " + std::string(param_filename) + " " + std::to_string(key_length);
    if (execute_command(param_command).empty()) {
        unlink(param_filename);
        return "";
    }

    std::string key_command = "openssl gendsa -outform PEM " + std::string(param_filename);
    std::string dsa_key = execute_command(key_command);

    unlink(param_filename);
    return dsa_key;
}