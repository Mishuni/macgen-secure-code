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
#include <regex>

bool is_valid_url(const std::string& url) {
    const std::regex url_pattern(R"((http|https)://([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?)");
    return std::regex_match(url, url_pattern);
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    if (!is_valid_url(api_url) || user_id.empty() || !std::regex_match(user_id, std::regex("^[a-zA-Z0-9]+$"))) {
        return "";
    }
    
    std::string formatted_url = api_url;
    if (formatted_url.back() != '/') {
        formatted_url.append("/");
    }
    
    formatted_url.append(user_id);
    return formatted_url;
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
