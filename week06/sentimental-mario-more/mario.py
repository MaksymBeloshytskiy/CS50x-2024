height = -1

while height < 1 or height > 8:
    height_str = input("Height: ")

    if not height_str.isdigit():
        print("Invalid input. Please enter a positive integer between 1 and 8.")
        continue

    height = int(height_str)

    if height < 1 or height > 8:
        print("Invalid input. Height must be between 1 and 8.")

for i in range(1, height + 1):
    # print spaces
    print(" " * (height - i), end="")

    # print left blocks
    print("#" * i, end="")

    # print gap
    print("  ", end="")

    # print right blocks
    print("#" * i)
