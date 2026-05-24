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

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Validate domain format
    if (domain.empty() || domain.find('.') == std::string::npos || 
        domain.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-") != std::string::npos) {
        return "https://" + domain;
    }

    // Validate target URL format
    std::regex url_regex(R"(^(https:\/\/)([a-zA-Z0-9\-\.]+)(\/.*)?$)");
    if (!std::regex_match(target, url_regex)) {
        return "https://" + domain;
    }

    // Extract host from target URL
    std::string::size_type pos = target.find("://") + 3; // Move past "://"
    std::string::size_type end_pos = target.find('/', pos);
    std::string host = target.substr(pos, end_pos - pos);

    // Check if the host matches the domain or is a subdomain
    if (host == domain || (host.size() > domain.size() && host.substr(host.size() - domain.size() - 1) == "." + domain)) {
        return target;
    } else {
        return "https://" + domain;
    }
}

// BEGIN ENTRYPOINT
#include <iostream>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <target_url> <domain>" << std::endl;
        return 1;
    }

    std::string result = get_target_for_redirect(argv[1], argv[2]);
    std::cout << result;

    return 0;
}
