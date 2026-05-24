
#include <string>
#include <cstdlib>
#include <cstdio>
#include <unistd.h>
#include <fcntl.h>

std::string execute_command(const std::string& command);

std::string create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return "";
    }
    close(fd);

    std::string command1 = "openssl dsaparam -out " + std::string(param_filename) + " 2048";
    std::string command2 = "openssl gendsa " + std::string(param_filename);

    std::string result1 = execute_command(command1);
    if (result1.empty()) {
        unlink(param_filename);
        return "";
    }

    std::string private_key = execute_command(command2);
    unlink(param_filename);

    if (private_key.empty()) {
        return "";
    }

    return private_key;
}