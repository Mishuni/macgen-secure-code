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
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>
#include <stdexcept>
#include <cctype>

std::string sanitize_input(const std::string &input) {
    std::string sanitized;
    for (char c : input) {
        if (isalnum(c)) {
            sanitized += c;
        }
    }
    return sanitized;
}

std::string html_encode(const std::string &data) {
    std::string encoded;
    for (char c : data) {
        switch (c) {
            case '&': encoded += "&amp;"; break;
            case '<': encoded += "&lt;"; break;
            case '>': encoded += "&gt;"; break;
            case '"': encoded += "&quot;"; break;
            case '\'': encoded += "&#39;"; break;
            default: encoded += c; break;
        }
    }
    return encoded;
}

std::string get_welcome_message(const std::string &username) {
    if (username.length() > 50) {
        throw std::invalid_argument("Username too long");
    }
    std::string sanitized_username = sanitize_input(username);
    std::string encoded_username = html_encode(sanitized_username);
    return "Welcome, " + encoded_username + "!";
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <username>\n";
        return 1;
    }

    std::string message = get_welcome_message(argv[1]);
    std::cout << message;

    return 0;
}
