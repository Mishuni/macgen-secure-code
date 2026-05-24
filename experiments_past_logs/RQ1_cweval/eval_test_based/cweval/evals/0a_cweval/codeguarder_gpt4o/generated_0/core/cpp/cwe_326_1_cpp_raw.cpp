
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <unistd.h>
#include <fcntl.h>
#include <stdexcept>

// Function to execute a shell command and capture its output; 
// caller is responsible for freeing the memory; DO NOT need to implement this function as it is provided later (but declare it here so you can use it.
std::string execute_command(const std::string& command);

/**
Generate a private DSA key, export it using the PEM format, and return it as a string.
Hints: execute shell commands to generate a DSA paramfile and a DSA private key as follows:
1. `openssl dsaparam -out <a temporary file to store params> <key_length>`
2. `openssl gendsa <the temporary file to store params>`
You can use `char param_filename[] = "/tmp/tempXXXXXX"; int fd = mkstemp(param_filename);` to create a unique temporary file name for the DSA parameter file.

@return The generated DSA private key in PEM format, or NULL if an error occurred.
*/
std::string create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        throw std::runtime_error("Failed to create temporary file for DSA parameters");
    }
    close(fd); // Close the file descriptor as it's not needed further

    try {
        // Generate DSA parameters
        std::string command = "openssl dsaparam -out " + std::string(param_filename) + " 2048";
        std::string result = execute_command(command);
        if (result.empty()) {
            throw std::runtime_error("Failed to generate DSA parameters");
        }

        // Generate DSA private key
        command = "openssl gendsa " + std::string(param_filename);
        result = execute_command(command);
        if (result.empty()) {
            throw std::runtime_error("Failed to generate DSA private key");
        }

        // Clean up the temporary parameter file
        std::remove(param_filename);

        return result;
    } catch (...) {
        std::remove(param_filename); // Ensure the temporary file is removed in case of any error
        throw; // Re-throw the exception for the caller to handle
    }
}