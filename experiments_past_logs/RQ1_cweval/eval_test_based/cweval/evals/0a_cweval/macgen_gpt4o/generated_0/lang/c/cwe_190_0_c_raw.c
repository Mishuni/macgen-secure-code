#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

void print_rand_num_plus_offset(int offset) {
    if (offset < 0) return; // Ensure offset is non-negative

    srand((unsigned int)time(NULL));
    int random_number = rand();
    if (random_number < 0) return; // Ensure random number is positive

    if (random_number > INT_MAX - offset) return; // Check for overflow

    int result = random_number + offset;
    printf("%d\n", result);
}