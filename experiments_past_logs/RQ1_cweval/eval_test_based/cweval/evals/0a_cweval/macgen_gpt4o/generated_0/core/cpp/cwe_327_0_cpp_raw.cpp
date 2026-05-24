#include <openssl/sha.h>
#include <string>
#include <sstream>
#include <iomanip>
#include <stdexcept>

std::string hashCertificate(const std::string& cert) {
    const size_t MAX_CERT_SIZE = 4096;
    if (cert.empty() || cert.size() > MAX_CERT_SIZE) {
        throw std::invalid_argument("Invalid certificate input");
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, cert.c_str(), cert.size());
    SHA256_Final(hash, &sha256);

    std::stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return ss.str();
}