from functions.get_files_info import get_files_info
import textwrap

def main():
    test_case = [
        ["calculator", "."],
        ["calculator", "pkg"],
        ["calculator", "/bin"],
        ["calculator", "../"],
    ]
    for [x, y] in test_case:
        result = get_files_info(x, y)
        dir = "current"
        if y != ".":
            dir = f"\"{y}\""
        print(f"Result for {dir} directory:")
        print(textwrap.indent(result, "\t"))

if __name__ == "__main__":
    main()