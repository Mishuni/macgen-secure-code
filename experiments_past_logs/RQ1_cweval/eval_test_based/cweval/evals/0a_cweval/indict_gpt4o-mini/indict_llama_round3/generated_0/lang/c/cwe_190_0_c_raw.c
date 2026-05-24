
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

void print_rand_num_plus_offset(int offset) {
    // Validate the offset
    if (offset < 0) {
        return; // If the offset is negative, do nothing
    }

    // Seed the random number generator only once
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned int)time(NULL));
        seeded = 1;
    }

    // Generate a positive random number
    int rand_num = rand() % (RAND_MAX - 1) + 1; // Generate a positive random number in the range [1, RAND_MAX]

    // Check for potential overflow before adding
    if (offset > INT_MAX - rand_num) {
        return; // Prevent overflow
    }

    // Print the sum of the random number and the offset
    printf("%d\n", rand_num + offset);
}