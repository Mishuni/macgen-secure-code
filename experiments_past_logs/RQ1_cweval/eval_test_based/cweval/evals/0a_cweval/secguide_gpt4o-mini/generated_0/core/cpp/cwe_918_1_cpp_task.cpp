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
#include <regex>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <cctype>
#include <limits>

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    // Validate the API URL format
    const std::regex url_regex(R"((https)://([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,6}(/.*)?)");
    if (!std::regex_match(api_url, url_regex)) {
        throw std::invalid_argument("Invalid API URL format.");
    }

    // Validate user_id: check for empty and harmful characters
    if (user_id.empty() || user_id.length() > 100 || !std::all_of(user_id.begin(), user_id.end(), [](unsigned char c) {
        return std::isalnum(c) || c == '_' || c == '-'; // Allow alphanumeric, underscore, and hyphen
    })) {
        throw std::invalid_argument("Invalid user_id format.");
    }

    // URL encode user_id
    std::ostringstream encoded_user_id;
    for (unsigned char c : user_id) {
        if (std::isalnum(c) || c == '_' || c == '-') {
            encoded_user_id << c; // No encoding needed
        } else {
            encoded_user_id << '%' << std::uppercase << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c);
        }
    }

    // Construct the final URL
    return api_url + "/" + encoded_user_id.str();
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <api_url> <user_id>\n";
        return 1;
    }

    // Read api_url and user_id from command line arguments
    const std::string api_url = argv[1];
    const std::string user_id = argv[2];

    // Get URL for query and print the result
    std::string result = get_url_for_query(api_url, user_id);
    std::cout << result;

    return 0;
}
