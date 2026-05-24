
#include <iostream>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

std::string execute_command(const std::string& command);

std::string create_dsa_key() {
    const int key_length = 2048; // Use a secure key length
    char param_filename[] = "/tmp/dsa_paramsXXXXXX"; // Template for temporary file
    int fd = mkstemp(param_filename); // Create a unique temporary file
    if (fd == -1) {
        throw std::runtime_error("Failed to create temporary file for DSA parameters");
    }
    close(fd); // Close the file descriptor, we only need the filename

    // Generate DSA parameters
    std::string param_command = "openssl dsaparam -out " + std::string(param_filename) + " " + std::to_string(key_length);
    if (system(param_command.c_str()) != 0) {
        unlink(param_filename); // Clean up the temporary file
        throw std::runtime_error("Failed to generate DSA parameters");
    }

    // Generate DSA private key
    std::string key_command = "openssl gendsa -out " + std::string(param_filename) + " " + param_filename;
    if (system(key_command.c_str()) != 0) {
        unlink(param_filename); // Clean up the temporary file
        throw std::runtime_error("Failed to generate DSA private key");
    }

    // Read the generated private key from the temporary file
    std::string private_key = execute_command("cat " + std::string(param_filename));
    
    unlink(param_filename); // Clean up the temporary file
    return private_key; // Return the DSA private key in PEM format
}