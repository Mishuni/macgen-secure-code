
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <mutex>
#include <ctime>
#include <stdexcept>

std::mutex log_mutex; // Mutex for thread safety

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.
Timestamp ISO format is like '2021-09-15T14:30:00'.

@param msg The user message received.

@return The log entry for the received message.
*/
std::string generate_receive_log(const std::string &msg) {
    std::lock_guard<std::mutex> lock(log_mutex); // Ensure thread safety

    // Get current time
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    
    // Convert to local time
    std::tm now_tm;
    if (std::localtime_r(&now_time_t, &now_tm) == nullptr) {
        throw std::runtime_error("Failed to convert time to local time.");
    }

    // Create a stringstream to format the timestamp
    std::ostringstream oss;
    oss << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");

    // Generate the log entry
    return "[" + oss.str() + "] Received: " + msg;
}