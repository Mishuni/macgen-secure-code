#include <iostream>
#include <string>
#include <memory>
#include <stdexcept>
#include <array>

std::string create_private_key() {
    const int key_length = 2048; // Fixed key length, can be adjusted as needed
    const int min_key_length = 1024;
    const int max_key_length = 4096;

    // Validate key length to prevent command injection
    if (key_length < min_key_length || key_length > max_key_length) {
        return ""; // Return empty string if key length is invalid
    }

    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";
    
    std::array<char, 128> buffer;
    std::string result;
    result.reserve(1024); // Reserve memory to optimize allocation

    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // Return empty string if pipe opening fails
    }

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    return result.empty() ? "" : result; // Return the key or empty string if an error occurred
}