
#include <string>
#include <ctime>
#include <iomanip>
#include <sstream>

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'. Timestamp ISO format is like '2021-09-15T14:30:00'.

@param msg The user message received.

@return The log entry for the received message.
*/
std::string generate_receive_log(const std::string &msg) {
    // Get the current time
    std::time_t now = std::time(nullptr);
    std::tm tm_now;
    gmtime_r(&now, &tm_now); // Use gmtime_r for thread safety

    // Format the timestamp in ISO 8601 format
    std::ostringstream oss;
    oss << std::put_time(&tm_now, "%Y-%m-%dT%H:%M:%S");

    // Construct the log entry
    std::string log_entry = "[" + oss.str() + "] Received: " + msg;
    return log_entry;
}