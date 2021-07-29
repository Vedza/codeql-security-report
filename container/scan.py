import os
import subprocess
import sys

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"


def print_yellow(txt):
    print(f"{YELLOW}{txt}{RESET}")


def print_red(txt):
    print(f"{RED}{txt}{RESET}")


def print_green(txt):
    print(f"{GREEN}{txt}{RESET}")


def runCodeQLScript(codeQL, language) -> str:
    print_yellow(
        "\nCreating the codeQL database. This might take some time depending on the size of the project...")

    # Check if results folder already exist, if not instead create it
    if not os.path.exists(f"{os.getenv('GITHUB_WORKSPACE')}/results"):
        print_yellow(
            f"Creating {os.getenv('GITHUB_WORKSPACE')}/results folder...")
        os.makedirs(f"{os.getenv('GITHUB_WORKSPACE')}/results")

    codeQL.execute_codeql_command(
        f'database create --language={language} {os.getenv("GITHUB_WORKSPACE")}/results/source_db -s {os.getenv("GITHUB_WORKSPACE")}')

    # if response.returncode == 0:
    print_green("\nCreated the database")
    # else:
    #     print_red("\nFailed to create the database")
    #     exit(1)

    codeQL.execute_codeql_command(f'database upgrade {os.getenv("GITHUB_WORKSPACE")}/results/source_db')

    # if response.returncode == 0:
    print_green("\nUpgraded the database")
    # else:
    #     print_red("\nFailed to upgrade the database")
    #     exit(2)

    print_yellow(
        "\nnRunning the Quality and Security rules on the project")

    codeQL.execute_codeql_command(
        f'database analyze {os.getenv("GITHUB_WORKSPACE")}/results/source_db --format=sarifv2.1.0 --output={os.getenv("GITHUB_WORKSPACE")}/results/issues.sarif {language}-security-and-quality.qls')

    # if response.returncode == 0:
    print_green("\nQuery execution successful")
    # else:
    #     print_red("\nQuery execution failed")
    #     exit(3)

    # print_yellow("The results are saved at ${2}/issues.sarif")
