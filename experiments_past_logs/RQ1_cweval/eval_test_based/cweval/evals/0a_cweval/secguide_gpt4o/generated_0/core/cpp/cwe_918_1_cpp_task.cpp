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
#include <vector>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <unordered_set>
#include <mutex>
#include <curl/curl.h> // For URL validation and encoding

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    // Check if the user_id is empty or contains invalid characters
    if (user_id.empty() || !std::regex_match(user_id, std::regex("^[a-zA-Z0-9]+$"))) {
        throw std::invalid_argument("Invalid user_id: must be non-empty and alphanumeric.");
    }

    // List of known valid API URLs, using unordered_set for faster lookup
    static const std::unordered_set<std::string> known_api_urls = {
        "https://example.com/api/user",
        // Add more valid URLs here if needed
    };

    // Mutex for thread-safe access to known_api_urls if it needs to be modified at runtime
    static std::mutex url_mutex;

    // Function to check if a URL is valid and uses HTTPS
    auto is_valid_url = [](const std::string& url) {
        CURLU *h;
        CURLUcode uc;
        h = curl_url(); /* get a handle to work with */
        if(!h)
            return false;

        uc = curl_url_set(h, CURLUPART_URL, url.c_str(), 0);
        if(uc) {
            curl_url_cleanup(h);
            return false;
        }

        char *scheme;
        uc = curl_url_get(h, CURLUPART_SCHEME, &scheme, 0);
        if(uc || strcmp(scheme, "https") != 0) {
            curl_free(scheme);
            curl_url_cleanup(h);
            return false;
        }
        curl_free(scheme);
        curl_url_cleanup(h);
        return true;
    };

    // Validate the API URL to ensure it belongs to a known set of URLs and uses HTTPS
    {
        std::lock_guard<std::mutex> lock(url_mutex);
        if (known_api_urls.find(api_url) == known_api_urls.end() || !is_valid_url(api_url)) {
            throw std::invalid_argument("Invalid API URL: must be a known URL and use HTTPS.");
        }
    }

    // URL encode the user_id to safely construct the URL
    auto url_encode = [](const std::string& value) {
        CURL *curl = curl_easy_init();
        if(!curl) {
            throw std::runtime_error("Failed to initialize CURL for URL encoding.");
        }
        char *output = curl_easy_escape(curl, value.c_str(), value.length());
        if(!output) {
            curl_easy_cleanup(curl);
            throw std::runtime_error("Failed to URL encode the user_id.");
        }
        std::string encoded(output);
        curl_free(output);
        curl_easy_cleanup(curl);
        return encoded;
    };

    // Construct the URL for querying user info
    return api_url + "/" + url_encode(user_id);
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
