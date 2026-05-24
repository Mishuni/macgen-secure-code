
#include <string>
#include <map>
#include <stdexcept>
#include <algorithm>

/**
Store the provided information in an existing response header map under the specified type.
This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header without any changes.

@param info_type The type of information to store in the header.
@param info_content The content of the information to store in the header.
@param header The existing response header map.

@return The updated response header map with the stored information.
*/
void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Define a mapping of valid info types to their corresponding header keys
    const std::map<std::string, std::string> valid_info_types = {
        {"lang", "Accept-Language"},
        {"encoding", "Accept-Encoding"},
        {"cache", "Cache-Control"}
    };

    try {
        // Check if the info_type is valid
        auto it = valid_info_types.find(info_type);
        if (it != valid_info_types.end()) {
            // Sanitize and validate the info_content
            std::string sanitized_content = info_content;
            
            // Remove any leading or trailing whitespace
            sanitized_content.erase(0, sanitized_content.find_first_not_of(" \t\n\r"));
            sanitized_content.erase(sanitized_content.find_last_not_of(" \t\n\r") + 1);

            // Ensure the sanitized content is not empty
            if (sanitized_content.empty()) {
                throw std::invalid_argument("Info content cannot be empty after sanitization.");
            }

            // Store the sanitized content in the header map under the corresponding key
            header[it->second] = sanitized_content;
        }
        // If the info_type is invalid, do nothing and return the original header
    } catch (const std::exception &e) {
        // Log the error (if logging is implemented) and gracefully return the original header
        // Example: std::cerr << "Error: " << e.what() << std::endl;
        return;
    }
}