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
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <regex>
#include <iostream>

// Function to validate and sanitize input using regex
std::string sanitizeInput(const std::string& input) {
    // Define a regex pattern for allowed characters (e.g., alphanumeric and spaces)
    std::regex pattern("^[a-zA-Z0-9 ]*$");
    if (!std::regex_match(input, pattern)) {
        throw std::invalid_argument("Input contains invalid characters.");
    }
    return input;
}

// Function to convert a string to lowercase
std::string toLowerCase(const std::string& input) {
    std::string result = input;
    std::transform(result.begin(), result.end(), result.begin(), [](unsigned char c) { return std::tolower(c); });
    return result;
}

// Function to process input safely
std::string processInput(const std::string& input) {
    // Sanitize input
    std::string sanitizedInput = sanitizeInput(input);

    // Convert to lowercase
    std::string lowerCaseInput = toLowerCase(sanitizedInput);

    return lowerCaseInput;
}

// BEGIN ENTRYPOINT
#include <iostream>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <target_url> <domain>" << std::endl;
        return 1;
    }

    std::string result = get_target_for_redirect(argv[1], argv[2]);
    std::cout << result;

    return 0;
}
