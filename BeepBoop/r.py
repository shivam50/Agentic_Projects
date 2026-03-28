password = input("Enter password")


def main(password):
    l = len(password)
    if l > 7:
        print("Great password there")
    elif l == 7:
        print("Password is OK, but not too strong")
    else:
        print("Your password is weak")

if __name__ == "__main__":
    main(password)
