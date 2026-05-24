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

bool searchPattern(const std::string& pattern, const std::string& content) {
    // Validate input to prevent potential security issues
    if (pattern.empty() || content.empty()) {
        return false;
    }

    // Check for excessively large input to prevent resource exhaustion
    const size_t maxAllowedSize = 1000000; // Example threshold, adjust as needed
    if (pattern.size() > maxAllowedSize || content.size() > maxAllowedSize) {
        return false;
    }

    // Perform the search
    return content.find(pattern) != std::string::npos;
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    std::string pattern = argv[1];
    std::string content = argv[2];

    if (searchPattern(pattern, content)) {
        std::cout << "true";
    } else {
        std::cout << "false";
    }

    return 0;
}
