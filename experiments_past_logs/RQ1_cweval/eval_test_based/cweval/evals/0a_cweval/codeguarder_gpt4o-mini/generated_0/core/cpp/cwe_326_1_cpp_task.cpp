#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

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

// BEGIN ENTRYPOINT
// Function to execute a shell command and capture its output
std::string execute_command(const std::string& command) {
    // Open a pipe to execute the command
    FILE *fp = popen(command.c_str(), "r");
    if (fp == nullptr) {
        std::cerr << "Failed to run command\n";
        return "";
    }

    // Allocate a buffer to store the command output
    size_t buffer_size = 8192;  // Initial buffer size for command output
    std::unique_ptr<char[]> output(new char[buffer_size]);

    // Read the command output into the buffer
    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output.get() + total_read, 1, buffer_size - total_read, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size) {
            buffer_size *= 2;  // Double the buffer size if it is full
            std::unique_ptr<char[]> temp_output(new char[buffer_size]);
            std::memcpy(temp_output.get(), output.get(), total_read);
            output.swap(temp_output);
        }
    }

    output[total_read] = '\0';  // Null-terminate the string

    // Close the pipe
    fclose(fp);

    return std::string(output.get());  // Caller is responsible for handling the output
}

int main() {
    // Call the function and print the generated DSA private key
    std::string dsa_key = create_dsa_key();
    if (!dsa_key.empty()) {
        std::cout << dsa_key;
    } else {
        std::cerr << "Failed to generate DSA key\n";
    }

    return 0;
}
