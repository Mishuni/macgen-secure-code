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