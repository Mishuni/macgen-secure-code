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
#include <ctime>
#include <mutex>
#include <stdexcept>

std::mutex log_mutex; // Mutex for thread safety

std::string sanitize_message(const std::string &msg) {
    if (msg.length() > 1024) { // Input validation: max length
        throw std::invalid_argument("Message is too long");
    }

    std::string sanitized_msg;
    sanitized_msg.reserve(msg.length() * 2); // Reserve space for efficiency

    for (char c : msg) {
        // Example sanitization: escape special characters
        if (c == '\n') {
            sanitized_msg += "\\n";
        } else if (c == '\r') {
            sanitized_msg += "\\r";
        } else if (c == '"') {
            sanitized_msg += "\\\"";
        } else if (c == '\t') {
            sanitized_msg += "\\t"; // Escape tab character
        } else if (c < 32 || c > 126) { // Control characters
            sanitized_msg += "[CTRL]"; // Replace control characters
        } else {
            sanitized_msg += c;
        }
    }
    return sanitized_msg;
}

std::string generate_receive_log(const std::string &msg) {
    std::lock_guard<std::mutex> lock(log_mutex); // Ensure thread safety

    // Get the current time as a time_point
    auto now = std::chrono::system_clock::now();
    
    // Convert to time_t for formatting
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    
    // Create a tm structure for formatting in UTC
    std::tm now_tm = *std::gmtime(&now_time_t);
    
    // Create a string stream to format the timestamp
    std::ostringstream timestamp_stream;
    timestamp_stream << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");

    // Sanitize the message
    std::string sanitized_msg = sanitize_message(msg);
    
    // Construct the log entry
    std::string log_entry = "[" + timestamp_stream.str() + "] Received: " + sanitized_msg;

    return log_entry;
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
