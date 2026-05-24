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
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>
#include <cctype>
#include <algorithm>
#include <stdexcept>
#include <regex>

const size_t MAX_USER_ID_LENGTH = 256;

bool is_valid_url(const std::string& url) {
    const std::regex url_regex(
        R"(^https?://([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?$)",
        std::regex::extended
    );
    return std::regex_match(url, url_regex);
}

std::string url_encode(const std::string& value) {
    std::string encoded;
    char hex_chars[] = "0123456789ABCDEF";
    for (unsigned char c : value) {
        if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            encoded += c;
        } else {
            encoded += '%';
            encoded += hex_chars[c >> 4];
            encoded += hex_chars[c & 15];
        }
    }
    return encoded;
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    if (user_id.empty() || user_id.length() > MAX_USER_ID_LENGTH) {
        return "";
    }

    if (!is_valid_url(api_url)) {
        return "";
    }

    std::string encoded_user_id = url_encode(user_id);
    return api_url + "/" + encoded_user_id;
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
