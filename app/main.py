import sys
import os


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_expand = command.split()
        if command_expand[0] == "exit":
            break
        elif command_expand[0] == "echo":
            print(" ".join(command_expand[1:]))
        elif command_expand[0] == "type":
            PATH = os.environ.get("PATH", "")
            match command_expand[1]:
                case "echo" | "exit" | "type":
                    print(f"{command_expand[1]} is a shell builtin")
                case _:
                    for dir in PATH.split(":"):
                        if os.path.exists(f"{dir}/{command_expand[1]}"):
                            print(f"{command_expand[1]} is {dir}/{command_expand[1]}")
                            break
                    else:
                        print(f"{command_expand[1]}: not found")
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
