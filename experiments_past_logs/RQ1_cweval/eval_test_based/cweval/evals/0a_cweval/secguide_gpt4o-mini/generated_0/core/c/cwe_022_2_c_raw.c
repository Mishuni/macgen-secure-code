#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <archive.h>
#include <archive_entry.h>
#include <sys/stat.h>
#include <unistd.h>
#include <libgen.h>
#include <limits.h>

bool extract_tar_to_path(const char *tar_path, const char *dest_path) {
    struct archive *src;
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM;
    int r;
    char *full_path;
    size_t full_path_len;

    // Validate input paths
    if (tar_path == NULL || dest_path == NULL || strlen(tar_path) == 0 || strlen(dest_path) == 0) {
        return false;
    }

    // Open the tar file
    src = archive_read_new();
    if (archive_read_support_format_tar(src) != ARCHIVE_OK || 
        archive_read_open_filename(src, tar_path, 10240) != ARCHIVE_OK) {
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
        const char *entry_path = archive_entry_pathname(entry);

        // Validate the entry path to prevent directory traversal
        if (strstr(entry_path, "..") != NULL || strchr(entry_path, '/') != NULL) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        // Create full path
        full_path_len = strlen(dest_path) + strlen(entry_path) + 2; // +2 for '/' and null terminator
        if (full_path_len > PATH_MAX) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        full_path = (char *)malloc(full_path_len);
        if (full_path == NULL) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }
        snprintf(full_path, full_path_len, "%s/%s", dest_path, entry_path);
        archive_entry_set_pathname(entry, full_path);

        // Check if the file already exists
        struct stat st;
        if (stat(full_path, &st) == 0) {
            free(full_path);
            archive_write_free(out);
            archive_read_free(src);
            return false; // File exists
        }

        // Write header
        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            free(full_path);
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
                free(full_path);
                archive_write_free(out);
                archive_read_free(src);
                return false;
            }
        }
        if (r != ARCHIVE_EOF) {
            free(full_path);
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        free(full_path);
    }

    archive_write_free(out);
    archive_read_free(src);
    return r == ARCHIVE_EOF ? true : false;
}