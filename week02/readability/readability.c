#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    // Main variables
    string txt = get_string("Text: ");

    int letters = 0;
    int words = 1;
    int sentences = 0;

    // Main procedure
    for (int i = 0; i < strlen(txt); i++)
    {
        if (isalpha(txt[i]))
        {
            letters++;
        }

        else if (isspace(txt[i]))
        {
            words++;
        }

        else if (txt[i] == '.' || txt[i] == '!' || txt[i] == '?')
        {
            sentences++;
        }
    }

    // Letters and sentences for index
    float L = (float) letters / (float) words * 100;
    float S = (float) sentences / (float) words * 100;

    // Index
    int index = round(0.0588 * L - 0.296 * S - 15.8);

    // Procedures of index
    if (index < 1)
    {
        printf("Before Grade 1\n");
    }

    else if (index > 16)
    {
        printf("Grade 16+\n");
    }

    else
    {
        printf("Grade %i\n", index);
    }
}
