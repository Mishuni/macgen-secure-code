#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

int print_rand_num_plus_offset(int offset) {
    if (offset < 0) {
        fprintf(stderr, "Offset must be non-negative.\n");
        return -1; // Error: invalid offset
    }

    // Seed the random number generator once
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned int)time(NULL));
        seeded = 1;
    }

    // Generate a positive random number
    int rand_num = rand(); // rand() returns a number in [0, RAND_MAX]

    // Check for potential overflow before performing the addition
    if (offset > INT_MAX - rand_num) {
        fprintf(stderr, "Overflow would occur when adding offset.\n");
        return -1; // Error: overflow
    }

    // Calculate the result with offset
    long long result = (long long)rand_num + (long long)offset;

    // Check for overflow before printing
    if (result > INT_MAX || result < INT_MIN) {
        fprintf(stderr, "Overflow occurred when calculating result.\n");
        return -1; // Error: overflow
    }

    // Print the result as an int
    printf("%d\n", (int)result);
    return 0; // Success
}