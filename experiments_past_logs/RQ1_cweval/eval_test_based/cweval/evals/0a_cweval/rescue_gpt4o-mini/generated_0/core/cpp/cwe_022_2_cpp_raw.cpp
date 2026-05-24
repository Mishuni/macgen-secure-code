
#include <archive.h>
#include <archive_entry.h>
#include <string>
#include <iostream>
#include <filesystem>

bool extract_archive(struct archive *src, const char *dest_path) {
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM;
    int r;
    char full_path[4096];

    // Initialize the archive writer
    out = archive_write_disk_new();
    if (!out) {
        return false;
    }
    archive_write_disk_set_options(out, flags);

    // Read and extract each entry
    while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
        // Create full path
        snprintf(full_path, sizeof(full_path), "%s/%s", dest_path, archive_entry_pathname(entry));
        archive_entry_set_pathname(entry, full_path);

        // Write header
        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            archive_write_free(out);
            return false;
        }

        // Copy data
        const void *buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
            if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                archive_write_free(out);
                return false;
            }
        }
        if (r != ARCHIVE_EOF) {
            archive_write_free(out);
            return false;
        }
    }

    archive_write_free(out);
    return r == ARCHIVE_EOF ? true : false;
}

bool extract_tar_to_path(const std::string& tar_path, const std::string& dest_path) {
    if (tar_path.empty() || dest_path.empty()) {
        return false; // Invalid input
    }

    // Validate and normalize paths
    std::filesystem::path tarFilePath(tar_path);
    std::filesystem::path destDirPath(dest_path);

    // Check if the tar file exists
    if (!std::filesystem::exists(tarFilePath) || !std::filesystem::is_regular_file(tarFilePath)) {
        return false; // Tar file does not exist or is not a regular file
    }

    // Ensure the destination directory exists
    if (!std::filesystem::exists(destDirPath)) {
        std::filesystem::create_directories(destDirPath);
    }

    // Open the tar file
    struct archive *src = archive_read_new();
    if (!src) {
        return false; // Failed to create archive object
    }

    // Open the tar file for reading
    if (archive_read_open_filename(src, tar_path.c_str(), 10240) != ARCHIVE_OK) {
        archive_read_free(src);
        return false; // Failed to open tar file
    }

    // Extract the archive
    bool result = extract_archive(src, dest_path.c_str());

    // Clean up
    archive_read_free(src);
    return result;
}