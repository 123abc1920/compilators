#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int add(int a, int b);

int main() {
    int a;
    int b;
    int i;
    char k[100];
    int m;
    int the_t[3];
    int y;
    
    a = (6 + 7);
    printf("%s\n", "result: ");
    printf("%d\n", a);
    printf("%d\n", add(1, 2));
    for (i = 1; i < 10; i++) {
        printf("%d\n", i);
    }
    a = 0;
    while (((a < 6) && 1)) {
        printf("%d\n", a);
        a = (a + 1);
    }
    b = 5;
    printf("%d\n", b);
    b = (b + 1);
    y = 0;
    while (1) {
        printf("%d\n", y);
        y = (y + 1);
        if ((y > 7)) {
            printf("%s\n", "stop");
            break;
        }
    }
    the_t[0] = 1;
    the_t[1] = 2;
    the_t[2] = 3;
    for (i = 1; i < 4; i++) {
        printf("%d\n", the_t[i - 1]);
    }
    m = (5 + "9");
    printf("%d\n", m);
    printf("%s\n", "input k:");
    char read_temp_0[100];
    fgets(read_temp_0, 100, stdin);
    read_temp_0[strcspn(read_temp_0, "\n")] = 0;
    strcpy(k, read_temp_0);
    printf("%s\n", "read:");
    printf("%s\n", k);
    return 0;
}

int add(int a, int b) {
    return (a + b);
}