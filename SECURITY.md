# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

The Rover Trust, Safety & Operations (TSO) team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:

**tso@rover.com**

Please include the following information in your report:

- Type of vulnerability (e.g., authentication bypass, injection, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.


## Best Practices for Users

When using this library:

- Keep your installation up to date with the latest version
- Review the changelog and security advisories regularly
- Use environment variables or secure credential management for API keys
- Never commit credentials to version control
- Follow the principle of least privilege when configuring API access

## Scope

This security policy applies to the `cinder` Python package and its dependencies as defined in `pyproject.toml`.
