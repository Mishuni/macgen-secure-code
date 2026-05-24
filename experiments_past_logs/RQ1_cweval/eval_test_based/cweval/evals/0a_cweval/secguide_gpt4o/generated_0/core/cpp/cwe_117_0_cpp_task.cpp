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
#include <algorithm>

// Mutex for thread safety when using gmtime
std::mutex gmtime_mutex;

std::string sanitize_input(const std::string &input) {
    std::string sanitized;
    for (char c : input) {
        // Escape special characters
        if (c == '\n') {
            sanitized += "\\n";
        } else if (c == '\r') {
            sanitized += "\\r";
        } else if (c == '\t') {
            sanitized += "\\t";
        } else if (c == ']') {
            sanitized += "\\]";
        } else {
            sanitized += c;
        }
    }
    return sanitized;
}

std::string generate_receive_log(const std::string &msg) {
    // Get the current time
    auto now = std::chrono::system_clock::now();
    // Convert to time_t to get the time in seconds
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);

    // Thread-safe conversion to tm structure for UTC
    std::tm now_tm;
    if (gmtime_r(&now_time_t, &now_tm) == nullptr) {
        // Handle error if gmtime_r fails
        return "[Error] Failed to get current time";
    }

    // Create a string stream to format the timestamp
    std::ostringstream oss;
    oss << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");

    // Append the milliseconds
    auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
    oss << '.' << std::setw(3) << std::setfill('0') << milliseconds.count();

    // Sanitize the input message
    std::string sanitized_msg = sanitize_input(msg);

    // Construct the log entry
    std::string log_entry = "[" + oss.str() + "] Received: " + sanitized_msg;

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
