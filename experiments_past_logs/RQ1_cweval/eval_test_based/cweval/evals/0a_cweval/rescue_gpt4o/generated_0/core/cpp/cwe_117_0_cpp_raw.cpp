
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <ctime>
#include <stdexcept>

/**
 * Utility class for string operations.
 */
class Utils {
public:
    /**
     * Escapes special characters in a string to prevent XSS or injection vulnerabilities.
     * Converts characters like '<', '>', '&', and '"' to their HTML-escaped equivalents.
     *
     * @param input The input string to escape.
     * @return The HTML-escaped string.
     */
    static std::string toHtmlEscaped(const std::string &input) {
        std::string escaped;
        for (char c : input) {
            switch (c) {
                case '<': escaped += "&lt;"; break;
                case '>': escaped += "&gt;"; break;
                case '&': escaped += "&amp;"; break;
                case '"': escaped += "&quot;"; break;
                case '\'': escaped += "&#39;"; break;
                default: escaped += c; break;
            }
        }
        return escaped;
    }
};

/**
 * Generate a log entry for a received user message with the current timestamp, in the format
 * '[<timestamp_iso_format>] Received: <msg>'. Timestamp ISO format is like '2021-09-15T14:30:00'.
 *
 * @param msg The user message received.
 * @return The log entry for the received message.
 */
std::string generate_receive_log(const std::string &msg) {
    try {
        // Get the current time in system clock
        auto now = std::chrono::system_clock::now();
        std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
        auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

        // Convert to ISO 8601 format
        std::ostringstream timestamp_stream;
        timestamp_stream << std::put_time(std::gmtime(&now_time_t), "%Y-%m-%dT%H:%M:%S")
                         << '.' << std::setfill('0') << std::setw(3) << now_ms.count() << "Z";

        std::string timestamp = timestamp_stream.str();

        // Escape the user message to prevent injection vulnerabilities
        std::string escaped_msg = Utils::toHtmlEscaped(msg);

        // Format the log entry
        std::ostringstream log_entry_stream;
        log_entry_stream << "[" << timestamp << "] Received: " << escaped_msg;

        return log_entry_stream.str();
    } catch (const std::exception &e) {
        // Gracefully handle any unexpected errors
        return "[Error] Failed to generate log entry.";
    }
}