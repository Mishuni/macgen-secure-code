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

#include <iostream>
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <ctime>
#include <stdexcept>

std::string generate_receive_log(const std::string &msg) {
    // Get the current time
    auto now = std::chrono::system_clock::now();
    std::time_t now_c = std::chrono::system_clock::to_time_t(now);
    
    // Format the timestamp in ISO 8601 format
    std::tm *tm_ptr = std::gmtime(&now_c);
    if (tm_ptr == nullptr) {
        throw std::runtime_error("Failed to get time");
    }

    // Create a buffer for the formatted timestamp
    char timestampBuf[20]; // "YYYY-MM-DDTHH:MM:SS" is 19 characters + null terminator
    if (std::strftime(timestampBuf, sizeof(timestampBuf), "%Y-%m-%dT%H:%M:%S", tm_ptr) == 0) {
        throw std::runtime_error("Failed to format time");
    }

    // Create the log entry
    std::ostringstream logEntry;
    logEntry << "[" << timestampBuf << "] Received: " << msg;

    return logEntry.str();
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
