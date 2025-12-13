def decimal_to_arb(decimal_num, order):
    hex_characters = "0123456789ABCDEF"
    if decimal_num == 0:
        return "0"

    final = ""
    while decimal_num > 0:
        remainder = decimal_num % order
        final = hex_characters[remainder] + final
        decimal_num //= order

    return final


# Binary
print("------\nbin")
print(decimal_to_arb(4, 2))

print(decimal_to_arb(4, 4))

# Hex
print("------\nhex")
print(decimal_to_arb(4000, 16))

# 0-7
print("------\n0-7")
print(decimal_to_arb(7, 8))
print(decimal_to_arb(65535, 16))
