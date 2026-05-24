#include <archive.h>
#include <archive_entry.h>
#include <string>
#include <cstring>
#include <limits.h>
#include <stdexcept>
#include <memory>

bool extract_tar_to_path(const std::string& tar_path, const std::string& dest_path) {
    struct archive *src = nullptr;
    struct archive *out = nullptr;
    struct archive_entry *entry = nullptr;
    int flags = ARCHIVE_EXTRACT_SECURE_NODOTDOT | ARCHIVE_EXTRACT_SECURE_SYMLINKS;
    int r;
    char full_path[PATH_MAX];

    try {
        // Initialize the archive reader
        src = archive_read_new();
        if (!src) {
            throw std::runtime_error("Failed to create archive reader");
        }
        archive_read_support_format_tar(src);

        // Open the tar file
        if (archive_read_open_filename(src, tar_path.c_str(), 10240) != ARCHIVE_OK) {
            throw std::runtime_error(archive_error_string(src));
        }

        // Initialize the archive writer
        out = archive_write_disk_new();
        if (!out) {
            throw std::runtime_error("Failed to create archive writer");
        }
        archive_write_disk_set_options(out, flags);

        // Read and extract each entry
        while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
            const char *entry_path = archive_entry_pathname(entry);

            // Create full path
            if (snprintf(full_path, sizeof(full_path), "%s/%s", dest_path.c_str(), entry_path) >= PATH_MAX) {
                throw std::runtime_error("Path length exceeds buffer size");
            }

            // Security check: Ensure the full path is within the destination directory
            char resolved_path[PATH_MAX];
            if (realpath(full_path, resolved_path) == nullptr) {
                throw std::runtime_error("Failed to resolve path");
            }
            if (strncmp(resolved_path, dest_path.c_str(), dest_path.length()) != 0 || 
                (resolved_path[dest_path.length()] != '/' && resolved_path[dest_path.length()] != '\0')) {
                throw std::runtime_error("Resolved path is outside the destination directory");
            }

            archive_entry_set_pathname(entry, full_path);

            // Write header
            r = archive_write_header(out, entry);
            if (r != ARCHIVE_OK) {
                throw std::runtime_error(archive_error_string(out));
            }

            // Copy data
            const void *buff;
            size_t size;
            la_int64_t offset;
            while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
                if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                    throw std::runtime_error(archive_error_string(out));
                }
            }
            if (r != ARCHIVE_EOF) {
                throw std::runtime_error(archive_error_string(src));
            }
        }

        if (r != ARCHIVE_EOF) {
            throw std::runtime_error(archive_error_string(src));
        }
    } catch (...) {
        if (out) archive_write_free(out);
        if (src) archive_read_free(src);
        return false;
    }

    archive_write_free(out);
    archive_read_free(src);
    return true;
}