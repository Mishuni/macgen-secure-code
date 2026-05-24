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
#include <cctype>
#include <stdexcept>
#include <sstream>
#include <iomanip>

std::string url_encode(const std::string& value) {
    std::ostringstream encoded;
    for (unsigned char c : value) {
        if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            encoded << c;
        } else {
            encoded << '%' << std::uppercase << std::setw(2) << std::setfill('0') << static_cast<int>(c);
        }
    }
    return encoded.str();
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    // Validate api_url
    if (api_url.empty() || api_url.find("://") == std::string::npos) {
        return ""; // Return empty string instead of throwing an exception
    }

    // Validate user_id
    if (user_id.empty() || !std::all_of(user_id.begin(), user_id.end(), [](unsigned char c) { return std::isalnum(c); })) {
        return "";
    }

    // Ensure api_url ends with a slash
    std::string valid_api_url = api_url;
    if (valid_api_url.back() != '/') {
        valid_api_url += "/";
    }

    // URL encode the user_id
    std::string encoded_user_id = url_encode(user_id);

    return valid_api_url + encoded_user_id;
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
