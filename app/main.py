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
        command, *params = command_full.split()
        match command:
            case "exit":
                break
            case "echo":  # must rewrite with builtin echo logic
                os.system(command_full)
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
                    os.system(command_full)
                else:
                    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
