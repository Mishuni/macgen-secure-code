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
#include <algorithm>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    const std::string protocol = "https://";
    std::regex url_regex(R"(https:\/\/([^\/]+)(\/.*)?)");
    std::smatch url_match;

    if (!std::regex_match(target, url_match, url_regex)) {
        return protocol + domain;
    }

    std::string target_domain = url_match[1].str();
    std::string lower_target_domain = target_domain;
    std::string lower_domain = domain;
    std::transform(lower_target_domain.begin(), lower_target_domain.end(), lower_target_domain.begin(), ::tolower);
    std::transform(lower_domain.begin(), lower_domain.end(), lower_domain.begin(), ::tolower);

    // Ensure the target domain is either exactly the same as the provided domain or a valid subdomain
    if (lower_target_domain == lower_domain || 
        (lower_target_domain.length() > lower_domain.length() && 
         lower_target_domain.compare(lower_target_domain.length() - lower_domain.length() - 1, lower_domain.length() + 1, "." + lower_domain) == 0)) {
        return target;
    }

    return protocol + domain;
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
