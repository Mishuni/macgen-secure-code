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
#include <jwt.h>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <openssl/buffer.h>
#include <nlohmann/json.hpp>

std::string base64_url_decode(const std::string& input) {
    std::string output;
    std::string padded_input = input;
    while (padded_input.size() % 4 != 0) {
        padded_input += '=';
    }
    std::string::size_type pos = 0;
    while ((pos = padded_input.find('-', pos)) != std::string::npos) {
        padded_input.replace(pos, 1, "+");
    }
    pos = 0;
    while ((pos = padded_input.find('_', pos)) != std::string::npos) {
        padded_input.replace(pos, 1, "/");
    }

    BIO* bio = BIO_new_mem_buf(padded_input.data(), padded_input.size());
    BIO* b64 = BIO_new(BIO_f_base64());
    bio = BIO_push(b64, bio);
    BIO_set_flags(bio, BIO_FLAGS_BASE64_NO_NL);
    char buffer[512];
    int decoded_length = BIO_read(bio, buffer, sizeof(buffer));
    BIO_free_all(bio);
    output.assign(buffer, decoded_length);
    return output;
}

bool verify_signature(const std::string& data, const std::string& signature, const std::string& key) {
    unsigned char hmac[EVP_MAX_MD_SIZE];
    unsigned int hmac_length;
    HMAC(EVP_sha256(), key.data(), key.size(), reinterpret_cast<const unsigned char*>(data.data()), data.size(), hmac, &hmac_length);
    std::string computed_signature(reinterpret_cast<char*>(hmac), hmac_length);
    return computed_signature == base64_url_decode(signature);
}

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    if (token.empty() || key.empty() || key.length() < 32) {
        return "{}";
    }

    std::vector<std::string> parts;
    std::stringstream ss(token);
    std::string item;
    while (std::getline(ss, item, '.')) {
        parts.push_back(item);
    }

    if (parts.size() != 3 || parts[0].empty() || parts[1].empty() || parts[2].empty()) {
        return "{}";
    }

    std::string header_json = base64_url_decode(parts[0]);
    std::string payload_json = base64_url_decode(parts[1]);
    std::string signature = parts[2];

    if (!verify_signature(parts[0] + "." + parts[1], signature, key)) {
        return "{}";
    }

    return payload_json;
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
