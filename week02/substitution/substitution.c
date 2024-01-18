#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

bool is_valid_key(string s);

int main(int argc, string argv[])
{
    // Limitting the number of elements to fit in terminal
    if (argc != 2)
    {
        printf("Usege: ./substitution key\n");
        return 1;
    }

    // Validation of key charachters in position 1 of array
    if (!is_valid_key(argv[1]))
    {
        printf("Key must contain 26 characters\n");
        return 1;
    }

    // Asking our user for text
    string s = get_string("plaintext: ");

    // Making a difference variable to calculate our ciphertext
    string difference = argv[1];

    // Cycle for checking difference between our key and the alphabet in ASCII
    for (int i = 'A'; i <= 'Z'; i++)
    {
        difference[i - 'A'] = toupper(difference[i - 'A']) - i; // Getting the element from our key and making a difference
    }

    printf("ciphertext: ");
    // Cycle for storing the value of valid key
    for (int i = 0, len = strlen(s); i < len; i++)
    {
        if (isalpha(s[i]))
        {
            s[i] = s[i] + difference[s[i] - (isupper(s[i]) ? 'A' : 'a')];
        }
        printf("%c", s[i]);
    }

    printf("\n");
}

bool is_valid_key(string s)
{
    int len = strlen(s);
    if (len != 26)
    {
        return false;
    }

    int freq[26] = {0};
    for (int i = 0; i < len; i++)
    {
        if (!isalpha(s[i]))
        {
            return false;
        }

        int index = toupper(s[i]) - 'A';
        if (freq[index] > 0)
        {
            return false;
        }
        freq[index]++;
    }

    return true;
}
