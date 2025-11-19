import sys

from analysis import orchestrate_analysis

if __name__ == "__main__":
    args = set(sys.argv)

    if len(args) == 0:
        print("No arguments provided")
        print("functionality: python main.py <command>")

    if "analysis" in args:
        orchestrate_analysis()
    elif "database" in args:
        pass
    elif "ui" in args:
        pass
    else:
        print("invalid command")
