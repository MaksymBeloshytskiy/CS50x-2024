import csv
import sys


def main():

    if len(sys.argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt")
        sys.exit()

    database_file = sys.argv[1]
    sequence_file = sys.argv[2]

    # Read STRs from database file
    strs = []
    with open(database_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        strs = reader.fieldnames[1:]

    # Read DNA sequence from file
    with open(sequence_file, 'r') as file:
        dna = file.read()

    # Count STR repetitions in DNA sequence
    counts = {}
    for str in strs:
        max_count = 0
        for i in range(len(dna)):
            count = 0
            while dna[i:i+len(str)] == str:
                count += 1
                i += len(str)
            if count > max_count:
                max_count = count
        counts[str] = max_count

    # Compare STR counts to individuals in database
    with open(database_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            match = True
            for str in strs:
                if int(row[str]) != counts[str]:
                    match = False
                    break
            if match:
                print(row['name'])
                sys.exit()

    print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
