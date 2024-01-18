#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    printf("What is your name?\n");
    char *name = (char *) malloc(100);

    if (name != NULL && scanf("%s", name) == 1)
    {
        printf("hello, %s\n", name);
        free(name);
        return 0;
    }
    else
        return 1;
}
