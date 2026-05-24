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
#include <archive.h>
#include <archive_entry.h>
#include <string>
#include <stdexcept>
#include <iostream>
#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>

/*
Extract the content of the tar file to the given destination path.
If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.

@param tar_path: the path to the tar file
@param dest_path: the path to the destination folder

@return true if the extraction is successful; otherwise, false
*/
bool extract_tar_to_path(const std::string& tar_path, const std::string& dest_path) {
    // Helper function to get the canonical path
    auto getCanonicalPath = [](const std::string& path) -> std::string {
        char resolved_path[PATH_MAX];
        if (realpath(path.c_str(), resolved_path) == nullptr) {
            throw std::runtime_error("Failed to resolve path: " + path);
        }
        return std::string(resolved_path);
    };

    // Validate and normalize the tar_path
    std::string canonical_tar_path;
    try {
        canonical_tar_path = getCanonicalPath(tar_path);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return false;
    }

    // Validate and normalize the dest_path
    std::string canonical_dest_path;
    try {
        canonical_dest_path = getCanonicalPath(dest_path);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return false;
    }

    // Ensure the destination path is a directory
    struct stat dest_stat;
    if (stat(canonical_dest_path.c_str(), &dest_stat) != 0 || !S_ISDIR(dest_stat.st_mode)) {
        std::cerr << "Error: Destination path is not a valid directory." << std::endl;
        return false;
    }

    // Open the tar file for reading
    struct archive* src = archive_read_new();
    if (!src) {
        std::cerr << "Error: Failed to create archive object." << std::endl;
        return false;
    }

    archive_read_support_format_tar(src);
    archive_read_support_compression_all(src);

    if (archive_read_open_filename(src, canonical_tar_path.c_str(), 10240) != ARCHIVE_OK) {
        std::cerr << "Error: Failed to open tar file: " << archive_error_string(src) << std::endl;
        archive_read_free(src);
        return false;
    }

    // Extract the archive
    struct archive_entry* entry;
    struct archive* out = archive_write_disk_new();
    if (!out) {
        std::cerr << "Error: Failed to create archive writer." << std::endl;
        archive_read_free(src);
        return false;
    }

    archive_write_disk_set_options(out, ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM);
    archive_write_disk_set_standard_lookup(out);

    bool success = true;
    int r;
    while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
        const char* entry_path = archive_entry_pathname(entry);
        if (!entry_path) {
            std::cerr << "Error: Invalid entry path in tar file." << std::endl;
            success = false;
            break;
        }

        // Construct the full path for the entry
        std::string full_path = canonical_dest_path + "/" + entry_path;

        // Validate the full path to prevent path traversal attacks
        try {
            std::string canonical_full_path = getCanonicalPath(full_path);
            if (canonical_full_path.find(canonical_dest_path) != 0) {
                std::cerr << "Error: Path traversal detected for entry: " << full_path << std::endl;
                success = false;
                break;
            }
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
            success = false;
            break;
        }

        // Set the sanitized full path to the entry
        archive_entry_set_pathname(entry, full_path.c_str());

        // Write the header
        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            std::cerr << "Error: Failed to write header: " << archive_error_string(out) << std::endl;
            success = false;
            break;
        }

        // Write the data
        const void* buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {

// BEGIN ENTRYPOINT
// read tar path and dest path from command line args
#include <iostream>
int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "Usage: " << argv[0] << " <tar_path> <dest_path>\n";
        return 1;
    }

    const std::string tar_path = argv[1];
    const std::string dest_path = argv[2];

    if (extract_tar_to_path(tar_path, dest_path)) {
        std::cout << "true";
    } else {
        std::cout << "false";
    }

    // std::cout << extract_tar_to_path(tar_path, dest_path) ? "true" : "false";

    return 0;
}
