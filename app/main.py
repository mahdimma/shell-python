import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_expand = command.split()
        if command_expand[0] == "exit":
            break
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
