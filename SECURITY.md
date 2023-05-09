# Security
We take the security of this software seriously. If you believe you found a security issue or a vulnerability in this software, please report it as described below.

## How to Report a Vulnerability
Please **do not** report a security issue or vulnerability through the public-facing GitHub Issues.

Instead, report the issue or vulnerability directly to the maintainers of this GitHub Action at **[d-dot-one[at]proton.
me](mailto:d-dot-one[at]proton.me)**. You will receive a response from us within 48 hours. If the issue is confirmed,
we will release a patch as soon as possible, depending on complexity but historically within a few days.

Please include the information below (as much as possible) to help us better understand the issue:

* Type of issue (ex. buffer overflow, remote code execution, authentication/authorization bypass, etc.)
* The location of the affected source code (tag/branch/commit or URL)
* Any special configuration required to reproduce the issue
* Step-by-step instructions to reproduce the issue
* Proof-of-concept or exploit code (if available)
* Impact of the issue, including how an attacker might exploit the issue

This information will be helpful for us to identify and correct the issue.

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| CVSS v3.0 | Supported Versions                        |
| --------- | ----------------------------------------- |
| 9.0-10.0  | Releases within the previous three months |
| 4.0-8.9   | Most recent release                       |
