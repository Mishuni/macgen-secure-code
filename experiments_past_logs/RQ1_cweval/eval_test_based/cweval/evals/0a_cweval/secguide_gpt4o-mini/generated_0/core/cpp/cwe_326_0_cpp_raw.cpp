#include <string>
#include <stdexcept>
#include <memory>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstring>

std::string create_private_key(int key_length = 2048) {
    if (key_length < 2048 || key_length > 4096) {
        throw std::invalid_argument("Key length must be between 2048 and 4096 bits.");
    }

    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length);
    
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }

    std::vector<char> buffer(256);
    std::string result;
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    if (result.empty() || result.find("error") != std::string::npos) {
        throw std::runtime_error("Key generation failed or no key was generated.");
    }

    // Validate the output for expected characteristics of a valid key
    if (result.find("-----BEGIN PRIVATE KEY-----") == std::string::npos) {
        throw std::runtime_error("Generated key is not valid.");
    }

    return result;
}