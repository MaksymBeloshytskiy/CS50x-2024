#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    // Making a defenition of BYTE and doing prepare moves for our buffer
    typedef uint8_t BYTE;
    BYTE buffer[512];
    int bytes_read, count = 0;
    char filename[8];

    // File management
    FILE *img = NULL;
    FILE *f = fopen(argv[1], "r");

    // Stupid user abilities
    if (argc != 2)
    {
        printf("Usage: ./recover IMAGE");
        return 1;
    }

    if (f == NULL)
    {
        printf("Usage: ./recover card.raw");
        return 1;
    }

    // Main doings with files
    while (1)
    {
        bytes_read = fread(buffer, sizeof(BYTE), 512, f);
        // First case
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && ((buffer[3] & 0xf0) == 0xe0))
        {
            if (count == 0)
            {
                sprintf(filename, "%03i.jpg", count);
                img = fopen(filename, "w");
                fwrite(buffer, sizeof(BYTE), bytes_read, img);
                count++;
            }

            else
            {
                fclose(img);
                sprintf(filename, "%03i.jpg", count);
                img = fopen(filename, "w");
                fwrite(buffer, sizeof(BYTE), bytes_read, img);
                count++;
            }
        }

        // Second case
        else if (count != 0)
        {
            fwrite(buffer, sizeof(BYTE), bytes_read, img);
            if (bytes_read == 0)
            {
                fclose(img);
                fclose(f);
                return 0;
            }
        }
    }
    // Closing files
    fclose(img);
    fclose(f);
}
