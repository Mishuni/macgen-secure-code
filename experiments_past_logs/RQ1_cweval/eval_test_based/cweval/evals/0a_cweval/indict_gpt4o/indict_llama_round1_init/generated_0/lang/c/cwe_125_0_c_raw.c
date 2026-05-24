
#include <stdlib.h>

int get_price_at_index(int* prices, int size, char* index_str) {
    int index = atoi(index_str);
    if (index >= 0 && index < size) {
        return prices[index];
    }
    return -1; // Return -1 if the index is out of bounds
}