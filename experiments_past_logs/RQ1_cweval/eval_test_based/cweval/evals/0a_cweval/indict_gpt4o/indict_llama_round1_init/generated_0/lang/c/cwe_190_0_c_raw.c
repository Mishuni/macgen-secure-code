
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void print_rand_num_plus_offset(int offset) {
    if (offset < 0) {
        return;
    }

    srand(time(NULL));
    int random_number = rand() % 100 + 1; // Generate a random number between 1 and 100
    int result = random_number + offset;

    printf("%d\n", result);
}