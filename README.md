# CodeQL Security Scan Action 

This action will run CodeQL rules on files in `$GITHUB_WORKSPACE` and checks for security issues. A markdown report is generated with the results and available in `$CODEQL_MD`

## Usage

Here is an action that will run on every pull request, scan all the files and post the result in a comment:

```yaml
name: CodeQL Security Scan
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      LANGUAGE: javascript
    steps:
      - uses: actions/checkout@v2
      - name: Run CodeQL scan
        uses: themenu/codeql-security-report@master
      - name: Comment PR
        uses: thollander/actions-comment-pull-request@master
        with:
          message: |
           ${{ env.CODEQL_MD }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Here is an action that will run on every pull request, scan only the files edited in the PR and post the result in a comment:

```yaml
name: CodeQL Security Scan
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      LANGUAGE: javascript
    steps:
      - uses: actions/checkout@v2
      
      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v13.1
        
      - name: Delete unedited files
        id: delete
        continue-on-error: true
        run: |
          for file in ${{ steps.changed-files.outputs.all_changed_and_modified_files }}; do
            edited="$edited ! -name ${file##*/}"
          done
          edited="${edited:1}"
          find $GITHUB_WORKSPACE $edited -type f -exec rm -f {} +
          ls -R $GITHUB_WORKSPACE
          if [[ "$edited" == *".js"* ]]; then
            exit 0
          fi
          exit 1
          
      - name: Run CodeQL scan
        if: steps.delete.outcome == 'success'
        uses: vedza/codeql-security-report@master
      - name: Comment PR
        if: steps.delete.outcome == 'success'
        uses: thollander/actions-comment-pull-request@main
        with:
          message: |
           ${{ env.CODEQL_MD }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```



### Docker image issue
The docker image of this action is based on [mcr.microsoft.com/cstsectools/codeql-container](https://github.com/microsoft/codeql-container). But because of some issue, I had to build my own image [vedza/codeql-github-action](codeql_base/Dockerfile), which use the same Dockerfile as [mcr.microsoft.com/cstsectools/codeql-container](https://github.com/microsoft/codeql-container).

So when the base image is updated, we will need to update the docker image to use the latest microsoft image.

### Use as Github Action or as CodeQL container

Our image run our script that scan and generate the markdown report only if no `$CODEQL_CLI_ARGS` is passed in env.

So you can still use this image the same way as [mcr.microsoft.com/cstsectools/codeql-container](https://github.com/microsoft/codeql-container) to run CodeQL queries if you want. 


### Ignore files or vulnerabilities

If you want to skip test on some files or vulnerabilities, you can add path and/or vulnerability `id` in a `.sastignore` file in the root of your project.

### Security Report

The security report is available in `$CODEQL_MD` as markdown.
It contains security issues split by priority, and issues in each priority level are sorted by score.
You can click on the file URL to see the exact piece of code causing the security issue.

Here is an example of what the markdown report look like for [NodeGoat](https://github.com/OWASP/NodeGoat):

<details><summary>NodeGoat</summary>

  # Security issues

  ## High Priority 
  <details><summary>Uncontrolled data used in network request</summary>

  **Score:** *9.1*
  **Definition**: *Sending network requests with user-controlled data allows for request forgery attacks.*
  **ID:** `js/request-forgery`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  The URL of this request depends on a user-provided value|[example/NodeGoat/app/routes/research.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/research.js#L16-L28)|Medium

  </details>
  <details><summary>Log injection</summary>

  **Score:** *7.8*
  **Definition**: *Building log entries from user-controlled sources is vulnerable to insertion of forged log entries by a malicious user.*
  **ID:** `js/log-injection`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  User-provided value flows to log entry|[example/NodeGoat/app/routes/session.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/session.js#L62)|Medium

  </details>
  <details><summary>Inefficient regular expression</summary>

  **Score:** *7.5*
  **Definition**: *A regular expression that requires exponential time to match certain inputs can be a performance bottleneck, and may be vulnerable to denial-of-service attacks.*
  **ID:** `js/redos`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  This part of the regular expression may cause exponential backtracking on strings containing many repetitions of '0'|[example/NodeGoat/app/routes/profile.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/profile.js#L59)|High

  </details>
  <details><summary>Polynomial regular expression used on uncontrolled data</summary>

  **Score:** *7.5*
  **Definition**: *A regular expression that can require polynomial time to match may be vulnerable to denial-of-service attacks.*
  **ID:** `js/polynomial-redos`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  This regular expression that depends on a user-provided value may run slow on strings with many repetitions of '0'|[example/NodeGoat/app/routes/profile.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/profile.js#L61)|High

  </details>
  <details><summary>Uncontrolled data used in path expression</summary>

  **Score:** *7.5*
  **Definition**: *Accessing paths influenced by users can allow an attacker to access unexpected resources.*
  **ID:** `js/path-injection`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  This path depends on a user-provided value|[example/NodeGoat/app/routes/index.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/index.js#L88)|High

  </details>


  ## Medium Priority
  <details><summary>Code injection</summary>

  **Score:** *6.1*
  **Definition**: *Interpreting unsanitized user input as code allows a malicious user arbitrary code execution.*
  **ID:** `js/code-injection`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  User-provided value flows to here and is interpreted as code|[example/NodeGoat/app/data/allocations-dao.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/data/allocations-dao.js#L78)|High
  User-provided value flows to here and is interpreted as code|[example/NodeGoat/app/routes/contributions.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/contributions.js#L32)|High
  User-provided value flows to here and is interpreted as code|[example/NodeGoat/app/routes/contributions.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/contributions.js#L33)|High
  User-provided value flows to here and is interpreted as code|[example/NodeGoat/app/routes/contributions.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/contributions.js#L34)|High

  </details>
  <details><summary>Server-side URL redirect</summary>

  **Score:** *6.1*
  **Definition**: *Server-side URL redirection based on unvalidated user input may cause redirection to malicious web sites.*
  **ID:** `js/server-side-unvalidated-url-redirection`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  Untrusted URL redirection due to user-provided value|[example/NodeGoat/app/routes/index.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/routes/index.js#L74)|High

  </details>
  <details><summary>DOM text reinterpreted as HTML</summary>

  **Score:** *6.1*
  **Definition**: *Reinterpreting text from the DOM as HTML can lead to a cross-site scripting vulnerability.*
  **ID:** `js/xss-through-dom`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  DOM text is reinterpreted as HTML without escaping meta-characters|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High

  </details>
  <details><summary>Unsafe jQuery plugin</summary>

  **Score:** *6.1*
  **Definition**: *A jQuery plugin that unintentionally constructs HTML from some of its options may be unsafe to use for clients.*
  **ID:** `js/unsafe-jquery-plugin`
  
  Title  | File | Precision  
  --------- | --------- | ---------
  Potential XSS vulnerability in the '$fntooltip' plugin|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  Potential XSS vulnerability in the '$fncollapse' plugin|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  Potential XSS vulnerability in the '$fnscrollspy' plugin|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High
  Potential XSS vulnerability in the '$fnscrollspy' plugin|[example/NodeGoat/app/assets/vendor/bootstrap/bootstrap.js](https://github.com/OWASP/NodeGoat/blob/e2dffdb8c7e988c10bacdccba14d6f0d352c5090/app/assets/vendor/bootstrap/bootstrap.js#L11)|High

  </details>
