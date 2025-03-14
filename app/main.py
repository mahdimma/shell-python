import sys
import os


def main():
    PATH = os.environ.get("PATH", "")
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_expand = command.split()
        match command_expand[0]:
            case "exit":
                break
            case "echo":
                print(" ".join(command_expand[1:]))
            case "type":
                match command_expand[1]:
                    case "echo" | "exit" | "type":
                        print(f"{command_expand[1]} is a shell builtin")
                    case _:
                        notFound = True
                        for dir in PATH.split(":"):
                            if os.path.exists(f"{dir}/{command_expand[1]}"):
                                print(
                                    f"{command_expand[1]} is {dir}/{command_expand[1]}"
                                )
                                notFound = False
                                break
                        if notFound:
                            print(f"{command_expand[1]}: not found")
            case _:
                notFound = True
                for dir in PATH.split(":"):
                    if os.path.exists(f"{dir}/{command_expand[0]}"):
                        os.system(f"{command}")
                        notFound = False
                        break
                if notFound:
                    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
