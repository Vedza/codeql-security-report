#!/usr/bin/env python3
import os
from scan import runCodeQLScript
import sys
from time import sleep
from libs.utils import get_env_variable, check_output_wrapper, get_logger
from libs.codeql import *
from convert import sarifToMD

CODEQL_HOME = get_env_variable('CODEQL_HOME')

# should we update the local copy of codeql-cli if a new version is available?
CHECK_LATEST_CODEQL_CLI = get_env_variable('CHECK_LATEST_CODEQL_CLI', True)

# should we update the local copy of codeql queries if a new version is available?
CHECK_LATEST_QUERIES = get_env_variable('CHECK_LATEST_QUERIES', True)

# if we are downloading new queries, should we precompile them
# (makes query execution faster, but building the container build slower).
PRECOMPILE_QUERIES = get_env_variable('PRECOMPILE_QUERIES', True)

# ql packs, requested to run, if any
CODEQL_CLI_ARGS = get_env_variable('CODEQL_CLI_ARGS', True)

# should we just exit after execution, or should we wait for user to stop container?
WAIT_AFTER_EXEC = get_env_variable('WAIT_AFTER_EXEC', True)

LANGUAGE = get_env_variable('LANGUAGE')


def main():
    # do the setup, if requested
    # get the parent directory of the script
    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    setup_script_args = ''
    if CHECK_LATEST_CODEQL_CLI:
        setup_script_args += ' --check-latest-cli'
    if CHECK_LATEST_QUERIES:
        setup_script_args += ' --check-latest-queries'
    if PRECOMPILE_QUERIES:
        setup_script_args += ' --precompile-latest-queries'

    run_result = check_output_wrapper(
        f"{scripts_dir}/setup.py {setup_script_args}",
        shell=True).decode("utf-8")

    codeql = CodeQL(CODEQL_HOME)

    # what command did the user ask to run?
    if CODEQL_CLI_ARGS == False or CODEQL_CLI_ARGS == ' ':
        # Run Scan if no CodeQL command was given.
        logger.info("Running codeQL full scan")
        runCodeQLScript(codeql, LANGUAGE)
        md = sarifToMD(f'{os.getenv("GITHUB_WORKSPACE")}/results/issues.sarif')

        # Put md content in $GITHUB_ENV file
        with open(f'{os.getenv("GITHUB_ENV")}', 'w') as f:
            f.write(f"CODEQL_MD<<\0\n{md}\n\0")


    else:
        run_result = codeql.execute_codeql_command(CODEQL_CLI_ARGS)
        print(run_result)

    if WAIT_AFTER_EXEC:
        logger.info("Wait forever specified, waiting...")
        while True:
            sleep(10)


logger = get_logger()
main()
