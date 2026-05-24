
#include <iostream>
#include <string>
#include <memory>
#include <array>
#include <stdexcept>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>

std::string create_private_key() {
    const int key_length = 2048; // You can change this value as needed
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    
    if (!pipe) {
        throw std::runtime_error("Failed to open pipe for command execution");
    }
    
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    
    if (result.empty()) {
        throw std::runtime_error("Failed to generate RSA private key");
    }
    
    // Securely clear the buffer
    std::memset(buffer.data(), 0, buffer.size());
    
    return result;
}