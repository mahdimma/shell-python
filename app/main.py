import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_expand = command.split()
        if command_expand[0] == "exit":
            break
        elif command_expand[0] == "echo":
            print(" ".join(command_expand[1:]))
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
