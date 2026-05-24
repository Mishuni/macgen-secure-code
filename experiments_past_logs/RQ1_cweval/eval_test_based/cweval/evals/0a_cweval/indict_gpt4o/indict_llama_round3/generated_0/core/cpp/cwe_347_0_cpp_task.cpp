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

#include <jwt-cpp/jwt.h>
#include <string>
#include <chrono>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    try {
        auto decoded = jwt::decode(token);

        // Create a verifier with the HS256 algorithm and the provided key
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key});

        // Verify the token
        verifier.verify(decoded);

        // Check for expiration
        if (decoded.has_expires_at() && decoded.get_expires_at() < std::chrono::system_clock::now()) {
            return "{}";
        }

        // Validate issuer and audience claims if they exist
        if (decoded.has_issuer() && decoded.get_issuer() != "expected_issuer") {
            return "{}";
        }
        if (decoded.has_audience() && !decoded.get_audience().count("expected_audience")) {
            return "{}";
        }

        // Return the payload as a JSON string
        return decoded.get_payload();
    } catch (const std::exception&) {
        return "{}";
    }
}

// BEGIN ENTRYPOINT
#include <cstdlib>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cout << "Usage: " << argv[0] << " <jwt_token> <key>" << std::endl;
        return 1;
    }

    std::string token = argv[1];
    std::string key = argv[2];

    std::string result = decode_json_web_token(token, key);
    std::cout << result;

    return 0;
}
