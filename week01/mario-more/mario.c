#include <stdio.h>

int main(void)
{
    int height = 0;
    while (height > 8 || height < 1)
    {
        printf("Height: ");
        scanf("%d", &height);
    }

    for (int row = 0; row < height; row++)
    {
        for (int space = 0; space < height - row - 1; space++)
        {
            printf(" ");
        }

        for (int character = 0; character <= row; character++)
        {
            printf("#");
        }

        printf("  ");

        for (int second_row = 0; second_row <= row; second_row++)
        {
            printf("#");
        }

        printf("\n");
    }
}
