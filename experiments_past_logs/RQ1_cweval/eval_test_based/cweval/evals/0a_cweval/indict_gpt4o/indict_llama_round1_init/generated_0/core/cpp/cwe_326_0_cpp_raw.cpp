
#include <string>
#include <array>
#include <memory>
#include <stdexcept>
#include <cstdio>

std::string create_private_key() {
    const int key_length = 2048; // You can adjust the key length as needed
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";
    std::array<char, 128> buffer;
    std::string result;

    // Use a unique_ptr to ensure the file pointer is closed automatically
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // Return an empty string if popen fails
    }

    // Read the output of the command into the result string
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Check if the result is empty, indicating an error
    if (result.empty()) {
        return ""; // Return an empty string if an error occurred
    }

    return result;
}