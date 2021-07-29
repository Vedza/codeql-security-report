FROM vedza/codeql-github-action:latest

COPY container /usr/local/startup_scripts/

ENTRYPOINT ["python3.8", "/usr/local/startup_scripts/startup.py"]