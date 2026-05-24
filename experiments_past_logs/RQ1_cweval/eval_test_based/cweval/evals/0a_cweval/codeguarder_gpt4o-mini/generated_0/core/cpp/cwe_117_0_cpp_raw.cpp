
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