import sys
import os
import readline
import subprocess

PATH_SEP = os.pathsep
PATH = os.environ.get("PATH", "")

BUILTINS = {
    "exit": "builtin",
    "type": "builtin",
    "echo": "builtin",
    "pwd": "builtin",
    "cd": "builtin",
}
COMMAND_TRIE = None


class TrieChar:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.value = None

    def insert(self, word, value):
        current_node = self
        for char in word:
            if char not in current_node.children:
                current_node.children[char] = TrieChar()
            current_node = current_node.children[char]
        current_node.is_end_of_word = True
        current_node.value = value

    def search(self, word):
        current_node = self
        for char in word:
            if char not in current_node.children:
                return None
            current_node = current_node.children[char]
        if current_node.is_end_of_word:
            return current_node.value
        return None

    def starts_with(self, prefix):
        current_node = self
        for char in prefix:
            if char not in current_node.children:
                return []
            current_node = current_node.children[char]
        return self._elements_with_prefix(current_node, prefix)

    def _elements_with_prefix(self, node, prefix):
        results = []
        if node.is_end_of_word:
            results.append(prefix)
        for char, next_node in node.children.items():
            results.extend(self._elements_with_prefix(next_node, prefix + char))
        return results


def populate_builtins_from_path(path):
    path = [p for p in path.split(PATH_SEP) if p]
    for current_path in path:
        files = []
        if os.path.exists(current_path):
            files = (
                file
                for file in os.listdir(current_path)
                if os.path.isfile(os.path.join(current_path, file))
            )
        for file in files:
            if file not in BUILTINS:
                BUILTINS[file] = os.path.join(current_path, file)


def create_command_trie():
    trie = TrieChar()
    for key, value in BUILTINS.items():
        trie.insert(key, value)
    return trie


def display_matches(substitution, matches, longest_match_length):
    matches = "  ".join(matches)
    print()
    print(matches, end=f"\n$ {substitution}")


def completer(text, state):
    options = COMMAND_TRIE.starts_with(text)
    if len(options) == 1:
        # If there is only one option, append a space to it
        options[0] += " "
    if state < len(options):
        return options[state]
    else:
        return None


def param_parser(param: str) -> list:
    params = []
    word = ""
    single_quote = False
    dobule_quote = False
    back_slash = False
    param = param.replace("''", "")
    param = param.replace('""', "")
    for char in param:
        if back_slash:
            word += char
            back_slash = False
        if char == " " and not (single_quote or dobule_quote):
            if word:
                params.append(word)
                word = ""
        elif char == "'" and not dobule_quote:
            if single_quote:
                params.append(word)
                word = ""
            single_quote = not single_quote
        elif char == '"' and not single_quote:
            if dobule_quote:
                params.append(word)
                word = ""
            dobule_quote = not dobule_quote
        elif char == "\\" and not (single_quote or dobule_quote):
            back_slash = True
        else:
            word += char
    if word:
        params.append(word)
    return params


def command_parser(command_full):
    append = command_full.find(">>")
    redirection = command_full.find(">")
    output_file = None
    error = False
    if append != -1:
        state = 2
        error = True if command_full[append - 1] == "2" else False
        command_full = command_full[: append - 1] + command_full[append:]
        command, output_file = command_full.split(">>")
        command = command.strip()
        output_file = output_file.strip()
    elif redirection != -1:
        state = 1
        error = True if command_full[redirection - 1] == "2" else False
        command_full = command_full[: redirection - 1] + command_full[redirection:]
        command, output_file = command_full.split(">")
        command = command.strip()
        output_file = output_file.strip()
    else:
        state = 0
        command = command_full
    command, *params = param_parser(command)
    return command, output_file, state, error, *params


def main():
    global COMMAND_TRIE
    populate_builtins_from_path(PATH)
    COMMAND_TRIE = create_command_trie()
    readline.set_completer_delims(" ")
    readline.set_completer(completer)
    readline.set_completion_display_matches_hook(display_matches)
    readline.parse_and_bind("tab: complete")

    while True:
        sys.stdout.write("$ ")
        command_full = input()
        if not command_full.strip():
            continue
        command, output_file, state, error_write, *params = command_parser(command_full)
        output_write = ""
        match command:
            case "exit":
                break
            case "echo":
                output_write = " ".join(params)
                output_write = (
                    output_write[1:-1]
                    if (output_write.startswith('"') or output_write.startswith("'"))
                    else output_write
                )
                if error_write:
                    print(output_write)
                    if state == 1:
                        with open(output_file, "w") as file:
                            pass
                    else:
                        with open(output_file, "a") as file:
                            pass
                else:
                    if state == 1:
                        with open(output_file, "w") as file:
                            print(output_write, file=file)
                    elif state == 2:
                        with open(output_file, "a") as file:
                            print(output_write, file=file)
                    else:
                        print(output_write)
            case "pwd":
                print(os.getcwd())
            case "cd":
                if not params:
                    print("cd: missing operand")
                    continue
                elif params[0].startswith("~"):
                    params[0] = os.path.expanduser(params[0])
                try:
                    os.chdir(params[0])
                except FileNotFoundError:
                    print(f"cd: {params[0]}: No such file or directory")
            case "type":
                if not params:
                    print("type: missing operand")
                    continue
                arg_command = params[0]
                if arg_command in BUILTINS:
                    if BUILTINS[arg_command] == "builtin":
                        print(f"{arg_command} is a shell builtin")
                    else:
                        print(f"{arg_command} is {BUILTINS[arg_command]}")
                else:
                    print(f"{arg_command}: not found")
            case _:
                if command in BUILTINS:
                    if state == 1:
                        with open(output_file, "w") as file:
                            if error_write:
                                subprocess.run([command, *params], stderr=file)
                            else:
                                subprocess.run([command, *params], stdout=file)
                    elif state == 2:
                        with open(output_file, "a") as file:
                            if error_write:
                                subprocess.run([command, *params], stderr=file)
                            else:
                                subprocess.run([command, *params], stdout=file)
                    else:
                        subprocess.run([command, *params])

                else:
                    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
