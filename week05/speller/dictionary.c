// Implements a dictionary's functionality

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 286182;

// Hash table
node *table[N];

// Number of words loaded into the dictionary
unsigned int word_count = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO
    unsigned int hashed = hash(word);
    node *cursor = table[hashed];

    // Traverse the linked list in the bucket
    while (cursor != NULL)
    {
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true; // Word found in the dictionary
        }
        cursor = cursor->next;
    }

    return false; // Word not found in the dictionary
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    unsigned int hash_value = 0;

    while (*word != '\0')
    {
        hash_value = (hash_value << 2) ^ tolower(*word);
        word++;
    }

    return hash_value % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    FILE *file = fopen(dictionary, "r");

    if (file == NULL)
    {
        return false;
    }

    char word[LENGTH + 1];

    while (fscanf(file, "%s", word) != EOF)
    {
        node *member = (node *) malloc(sizeof(node));
        if (member == NULL)
        {
            fclose(file);
            return false;
        }

        // Copy the word into the new node
        strcpy(member->word, word);

        // Insert the new node at the beginning of the linked list in the corresponding bucket
        unsigned int index = hash(word);
        member->next = table[index];
        table[index] = member;

        word_count++;
    }

    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    return word_count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // TODO
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        while (cursor != NULL)
        {
            node *temp = cursor;
            cursor = cursor->next;
            free(temp);
        }
    }

    return true;
}
