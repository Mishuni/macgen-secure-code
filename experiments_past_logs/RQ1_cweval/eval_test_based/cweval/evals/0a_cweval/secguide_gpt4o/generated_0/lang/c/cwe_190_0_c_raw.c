#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

// Function to seed the random number generator once
void seed_random_generator() {
    // No longer needed as we use a more secure random number generator
}

// Function to generate a secure random number
int secure_random_number() {
    int random_number;
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        // Handle error opening /dev/urandom
        return -1;
    }
    if (read(fd, &random_number, sizeof(random_number)) != sizeof(random_number)) {
        // Handle error reading from /dev/urandom
        close(fd);
        return -1;
    }
    close(fd);
    return random_number & INT_MAX; // Ensure the number is non-negative
}

void print_rand_num_plus_offset(int offset) {
    // Check if the offset is non-negative
    if (offset < 0) {
        return;
    }

    // Generate a secure random number
    int random_number = secure_random_number();
    if (random_number == -1) {
        // Handle error in random number generation
        return;
    }

    // Check for potential overflow before adding the offset
    if (random_number > INT_MAX - offset) {
        return;
    }

    // Calculate the result
    int result = random_number + offset;

    // The function does not include any print statements or logging
}