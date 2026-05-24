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
#include <string>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <fcntl.h>
#include <stdexcept>
#include <sstream>
#include <filesystem>
#include <vector>
#include <memory>

std::string execute_command(const std::string& command);

std::string create_dsa_key() {
    const int key_length = 2048; // Example key length
    std::string temp_dir = std::filesystem::temp_directory_path().string();
    std::string param_filename = (temp_dir + "/tempXXXXXX");
    int fd = mkstemp(&param_filename[0]);
    if (fd == -1) {
        throw std::runtime_error("Error creating temporary file");
    }
    close(fd);

    // Validate key_length
    if (key_length <= 0) {
        unlink(param_filename.c_str());
        throw std::invalid_argument("Invalid key length");
    }

    // Generate DSA parameters
    std::string param_command = "openssl dsaparam -out " + param_filename + " " + std::to_string(key_length);
    if (execute_command(param_command).empty()) {
        unlink(param_filename.c_str()); // Clean up
        throw std::runtime_error("Error generating parameters");
    }

    // Generate DSA private key
    std::string key_filename = (temp_dir + "/dsa_private_key_" + std::to_string(getpid()) + ".pem");
    std::string key_command = "openssl gendsa -out " + key_filename + " " + param_filename;
    if (execute_command(key_command).empty()) {
        unlink(param_filename.c_str()); // Clean up
        throw std::runtime_error("Error generating private key");
    }

    // Read the private key from the file
    std::unique_ptr<FILE, decltype(&fclose)> key_file(fopen(key_filename.c_str(), "r"), &fclose);
    if (!key_file) {
        unlink(param_filename.c_str()); // Clean up
        unlink(key_filename.c_str()); // Clean up
        throw std::runtime_error("Error opening key file");
    }

    std::string private_key;
    std::vector<char> buffer(256);
    while (fgets(buffer.data(), buffer.size(), key_file.get())) {
        private_key += buffer.data();
    }

    unlink(param_filename.c_str()); // Clean up
    unlink(key_filename.c_str()); // Clean up

    return private_key;
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
