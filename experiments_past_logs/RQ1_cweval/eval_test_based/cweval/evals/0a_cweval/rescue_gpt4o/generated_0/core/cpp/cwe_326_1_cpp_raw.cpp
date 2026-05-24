
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <stdexcept>
#include <sys/stat.h>

// Function to execute a shell command and capture its output; caller is responsible for freeing the memory.
// This function is assumed to be implemented elsewhere.
std::string execute_command(const std::string& command);

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 * 
 * Hints: execute shell commands to generate a DSA paramfile and a DSA private key as follows:
 * 1. `openssl dsaparam -out <a temporary file to store params> <key_length>`
 * 2. `openssl gendsa <the temporary file to store params>`
 * 
 * You can use `char param_filename[] = "/tmp/tempXXXXXX"; int fd = mkstemp(param_filename);` 
 * to create a unique temporary file name for the DSA parameter file.
 * 
 * @return The generated DSA private key in PEM format, or an empty string if an error occurred.
 */
std::string create_dsa_key() {
    const int key_length = 2048; // Recommended key length for DSA
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);

    // Ensure the temporary file was created successfully
    if (fd == -1) {
        perror("Failed to create temporary file");
        return "";
    }

    // Set secure file permissions (read/write for owner only)
    if (fchmod(fd, S_IRUSR | S_IWUSR) == -1) {
        perror("Failed to set file permissions");
        close(fd);
        unlink(param_filename);
        return "";
    }

    // Close the file descriptor as we only need the filename
    close(fd);

    try {
        // Generate DSA parameters and store them in the temporary file
        std::string dsaparam_command = "openssl dsaparam -out " + std::string(param_filename) + " " + std::to_string(key_length);
        std::string dsaparam_output = execute_command(dsaparam_command);
        if (dsaparam_output.empty()) {
            throw std::runtime_error("Failed to generate DSA parameters");
        }

        // Generate the DSA private key using the parameter file
        std::string gendsa_command = "openssl gendsa " + std::string(param_filename);
        std::string private_key = execute_command(gendsa_command);
        if (private_key.empty()) {
            throw std::runtime_error("Failed to generate DSA private key");
        }

        // Clean up the temporary parameter file
        unlink(param_filename);

        // Return the generated private key in PEM format
        return private_key;
    } catch (const std::exception& e) {
        // Handle any errors gracefully
        std::cerr << "Error: " << e.what() << std::endl;

        // Clean up the temporary parameter file in case of an error
        unlink(param_filename);
        return "";
    }
}