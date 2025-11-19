import sys
from tokenize import STAR

from analysis import orchestrate_analysis
from database import orchestrate_database_migration
from tinker import start_ui

if __name__ == "__main__":
    args = set(sys.argv)

    if len(args) == 0:
        print("No arguments provided")
        print("functionality: python main.py <command>")

    if "analysis" in args:
        orchestrate_analysis()
    elif "database" in args:
        orchestrate_database_migration()
    elif "ui" in args:
        start_ui()
    else:
        print("invalid command")
