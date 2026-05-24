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
#include <chrono>
#include <iomanip>
#include <sstream>
#include <stdexcept>

std::string generate_receive_log(const std::string &msg) {
    try {
        auto now = std::chrono::system_clock::now();
        auto now_time_t = std::chrono::system_clock::to_time_t(now);
        auto now_tm = *std::localtime(&now_time_t);

        std::ostringstream oss;
        oss << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");
        std::string timestamp = oss.str();

        // Enhanced sanitization: replace newline and other potentially harmful characters
        std::string sanitized_msg;
        for (char c : msg) {
            switch (c) {
                case '\n': sanitized_msg += "\\n"; break;
                case '\r': sanitized_msg += "\\r"; break;
                case '\t': sanitized_msg += "\\t"; break;
                case '\\': sanitized_msg += "\\\\"; break;
                case '\"': sanitized_msg += "\\\""; break;
                case '\'': sanitized_msg += "\\\'"; break;
                default: sanitized_msg += c; break;
            }
        }

        // Limit the length of the message to prevent performance issues
        const size_t max_length = 1000;
        if (sanitized_msg.length() > max_length) {
            sanitized_msg = sanitized_msg.substr(0, max_length) + "...";
        }

        return "[" + timestamp + "] Received: " + sanitized_msg;
    } catch (const std::exception &e) {
        throw std::runtime_error("Failed to generate log entry: " + std::string(e.what()));
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <message>\n";
        return EXIT_FAILURE;
    }

    // Ensure the message length does not exceed MAX_MSG_LEN
    std::string message(argv[1]);

    // Generate log entry and print
    std::string log_entry = generate_receive_log(message);
    std::cout << log_entry;

    return EXIT_SUCCESS;
}
