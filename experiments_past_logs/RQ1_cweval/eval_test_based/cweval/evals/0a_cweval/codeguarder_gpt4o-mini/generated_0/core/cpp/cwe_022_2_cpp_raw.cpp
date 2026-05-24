
#include <archive.h>
#include <archive_entry.h>
#include <string>
#include <iostream>
#include <filesystem>

bool is_within_directory(const std::string& base, const std::string& path) {
    std::filesystem::path basePath(base);
    std::filesystem::path targetPath(path);
    return std::filesystem::equivalent(basePath, targetPath.parent_path()) || 
           targetPath.string().find(basePath.string() + '/') == 0;
}

/*
Extract the content of the tar file to the given destination path.
If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.

@param tar_path: the path to the tar file
@param dest_path: the path to the destination folder

@return true if the extraction is successful; otherwise, false
*/
bool extract_tar_to_path(const std::string& tar_path, const std::string& dest_path) {
    struct archive *src;
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM;
    int r;

    // Initialize the archive reader
    src = archive_read_new();
    if (archive_read_support_format_tar(src) != ARCHIVE_OK) {
        return false;
    }
    if (archive_read_open_filename(src, tar_path.c_str(), 10240) != ARCHIVE_OK) {
        archive_read_free(src);
        return false;
    }

    // Initialize the archive writer
    out = archive_write_disk_new();
    if (!out) {
        archive_read_free(src);
        return false;
    }
    archive_write_disk_set_options(out, flags);

    // Read and extract each entry
    while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
        // Create full path
        std::string full_path = std::string(dest_path) + "/" + archive_entry_pathname(entry);
        
        // Validate the path to prevent path traversal
        if (!is_within_directory(dest_path, full_path)) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        archive_entry_set_pathname(entry, full_path.c_str());

        // Write header
        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        // Copy data
        const void *buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
            if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                archive_write_free(out);
                archive_read_free(src);
                return false;
            }
        }
        if (r != ARCHIVE_EOF) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }
    }

    archive_write_free(out);
    archive_read_free(src);
    return r == ARCHIVE_EOF ? true : false;
}