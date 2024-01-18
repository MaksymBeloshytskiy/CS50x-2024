card_number = input("Number: ")

# Check if input is a valid credit card number
if not card_number.isdigit():
    print("INVALID")
    exit()

if len(card_number) < 13 or len(card_number) > 16:
    print("INVALID")
    exit()

# Calculate checksum using Luhn's algorithm
sum_digits = 0
for i in range(len(card_number) - 1, -1, -1):
    digit = int(card_number[i])

    if (len(card_number) - i) % 2 == 0:
        digit *= 2

        if digit > 9:
            digit -= 9

    sum_digits += digit

# Sum validation
if sum_digits % 10 != 0:
    print("INVALID")
    exit()

# Check if card number is valid and print card type
if card_number[0] == '4' and (len(card_number) == 13 or len(card_number) == 16):
    print("VISA")
elif card_number[0:2] in ('34', '37') and len(card_number) == 15:
    print("AMEX")
elif card_number[0:2] in ('51', '52', '53', '54', '55') and len(card_number) == 16:
    print("MASTERCARD")
else:
    print("INVALID")
