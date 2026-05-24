
#include <iostream>
#include <string>
#include <stdexcept>
#include <array>
#include <memory>
#include <cstdio>
#include <stdexcept>

std::string create_private_key() {
    const int key_length = 2048; // Example key length
    std::array<char, 128> buffer;
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    // Use popen to execute the command and read the output
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }

    // Read the output from the command
    std::string result;
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Check if the result is empty, indicating an error occurred
    if (result.empty()) {
        throw std::runtime_error("Failed to generate RSA private key.");
    }

    return result;
}