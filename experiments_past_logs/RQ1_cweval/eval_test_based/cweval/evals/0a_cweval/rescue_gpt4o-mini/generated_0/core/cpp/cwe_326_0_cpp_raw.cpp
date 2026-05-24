
#include <iostream>
#include <string>
#include <memory>
#include <stdexcept>
#include <cstdio>
#include <array>

std::string create_private_key() {
    const int key_length = 2048; // Example key length
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    // Use a buffer to capture the output
    std::array<char, 128> buffer;
    std::string result;

    // Open a pipe to the command
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return NULL; // Return NULL if the pipe could not be opened
    }

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Check if the result is empty, indicating an error
    if (result.empty()) {
        return NULL; // Return NULL if no key was generated
    }

    return result; // Return the generated RSA private key in PEM format
}