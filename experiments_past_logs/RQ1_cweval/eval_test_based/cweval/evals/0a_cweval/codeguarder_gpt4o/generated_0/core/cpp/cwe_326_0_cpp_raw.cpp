
#include <iostream>
#include <string>
#include <array>
#include <memory>
#include <stdexcept>

std::string create_private_key() {
    const int key_length = 2048; // Secure key length
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);

    if (!pipe) {
        return ""; // Return empty string on error
    }

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    return result.empty() ? "" : result; // Return empty string if result is empty
}