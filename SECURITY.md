# Security Policy

## Reporting a vulnerability

Please report security issues privately, not in a public issue.

Use GitHub's **[Report a vulnerability](https://github.com/FROWNINGdev/AutomateExcelTasks/security/advisories/new)** button (Security → Advisories) to open a private report. You will get an acknowledgement within a few days.

These utilities open spreadsheet files with `openpyxl` / `pandas`. When reporting, useful cases include:

- a crafted `.xlsx` / `.xlsm` that triggers unsafe file writes outside the target directory;
- formula or path handling that lets an input file reach the filesystem or shell;
- a dependency advisory that affects a pinned version here.

Please attach a minimal sample file that reproduces the issue where possible.

## Supported versions

Only the latest commit on `master` is supported.
