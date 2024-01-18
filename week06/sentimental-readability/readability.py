text = input("Text: ")

# Count number of letters, words, and sentences in input text
num_letters = sum(c.isalpha() for c in text)
num_words = len(text.split())
num_sentences = len([c for c in text if c in ['.', '!', '?']])

# Calculate Coleman-Liau index
L = num_letters / num_words * 100
S = num_sentences / num_words * 100
index = round(0.0588 * L - 0.296 * S - 15.8)

# Print grade level based on Coleman-Liau index
if index < 1:
    print("Before Grade 1")
elif index >= 16:
    print("Grade 16+")
else:
    print("Grade", index)
