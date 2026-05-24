#include <cstdio>
#include <string>
#include <array>
#include <memory>

std::string create_private_key() {
    const int key_length = 2048; // Define the key length
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";
    std::array<char, 128> buffer;
    std::string result;

    // Open a pipe to execute the command
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return "";
    }

    // Read the output of the command into the buffer
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Check for errors during command execution
    if (pclose(pipe.release()) != 0) {
        return "";
    }

    return result;
}