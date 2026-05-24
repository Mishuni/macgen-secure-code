
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void print_rand_num_plus_offset(int offset) {
    if (offset < 0) {
        return; // If the offset is negative, do nothing
    }
    
    // Seed the random number generator
    srand((unsigned int)time(NULL));
    
    // Generate a positive random number
    int rand_num = rand() % (RAND_MAX + 1); // RAND_MAX is the maximum value returned by rand()
    
    // Print the sum of the random number and the offset
    printf("%d\n", rand_num + offset);
}