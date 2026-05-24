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
#include <openssl/hmac.h>
#include <openssl/rand.h>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include <stdexcept>

/*
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssh libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
std::string hashCertificate(const std::string& cert) {
    // Retrieve the secret key from a secure source, e.g., environment variable or secure vault
    const char* secretKey = getenv("HMAC_SECRET_KEY");
    if (!secretKey) {
        throw std::runtime_error("Secret key not found");
    }

    // Compute the HMAC-SHA-256 hash
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hashLen = 0;

    HMAC_CTX* ctx = HMAC_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create HMAC context");
    }

    if (HMAC_Init_ex(ctx, secretKey, strlen(secretKey), EVP_sha256(), nullptr) != 1 ||
        HMAC_Update(ctx, reinterpret_cast<const unsigned char*>(cert.data()), cert.size()) != 1 ||
        HMAC_Final(ctx, hash, &hashLen) != 1) {
        HMAC_CTX_free(ctx);
        throw std::runtime_error("Failed to compute HMAC");
    }

    HMAC_CTX_free(ctx);

    // Convert the hash to a hexadecimal string
    std::ostringstream oss;
    for (unsigned int i = 0; i < hashLen; ++i) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }

    return oss.str();
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <certificate>" << std::endl;
        std::exit(1);
    }

    std::string hashedCert = hashCertificate(argv[1]);
    std::cout << hashedCert;

    return 0;
}
