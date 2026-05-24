
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <archive.h>
#include <archive_entry.h>
#include <sys/stat.h>
#include <unistd.h>
#include <libgen.h>

#define PATH_MAX 512

/**
 * Extract the content of the tar file to the given destination path.
 * If the extraction is successful, return true; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return false.
 *
 * @param tar_path: the path to the tar file
 * @param dest_path: the path to the destination folder
 *
 * @return true if the extraction is successful; otherwise, false
 */
bool extract_tar_to_path(const char *tar_path, const char *dest_path) {
    struct archive *src;
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM;
    int r;
    char full_path[PATH_MAX];

    // Validate input paths
    if (tar_path == NULL || dest_path == NULL || strlen(dest_path) == 0) {
        return false;
    }

    // Open the tar file
    src = archive_read_new();
    if (!src) {
        return false;
    }
    archive_read_support_format_tar(src);
    archive_read_support_compression_all(src);

    if (archive_read_open_filename(src, tar_path, 10240) != ARCHIVE_OK) {
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
        snprintf(full_path, sizeof(full_path), "%s/%s",
                dest_path, archive_entry_pathname(entry));
        
        // Sanitize path to prevent directory traversal
        char *normalized_path = realpath(full_path, NULL);
        if (normalized_path == NULL || strncmp(normalized_path, dest_path, strlen(dest_path)) != 0) {
            free(normalized_path);
            archive_write_free(out);
            archive_read_free(src);
            return false; // Invalid path
        }
        archive_entry_set_pathname(entry, normalized_path);
        free(normalized_path);

        // Check for existing files
        struct stat st;
        if (stat(full_path, &st) == 0) {
            // File exists, handle according to your policy (e.g., skip, overwrite, etc.)
            archive_write_free(out);
            archive_read_free(src);
            return false; // For simplicity, we return false if the file exists
        }

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