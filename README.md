# GitHub Repository Downloader

A simple Python utility to download all files from a GitHub repository and concatenate them into a single text file.

## Features

- Downloads all text files from a GitHub repository
- Recursively traverses all directories
- Skips binary files like images, PDFs, executables, etc.
- Combines all downloaded files into a single text file with clear separators
- Auto-detects the repository's default branch
- Robust error handling to continue processing even if some files fail

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jonbrantingham/github-repo-downloader.git
cd github-repo-downloader
```

2. Install the required packages:
```bash
pip install requests
```

## Usage

### Basic Usage

```bash
python github_downloader.py [owner] [repo]
```

Where:
- `owner` is the GitHub username or organization that owns the repository
- `repo` is the name of the repository

For example:
```bash
python github_downloader.py jonbrantingham github-repo-downloader
```

This will create a file called `combined_output.txt` in the current directory containing all the text files from the repository.

### Advanced Options

```bash
python github_downloader.py [owner] [repo] --branch [branch] --output [output_file]
```

Additional parameters:
- `--branch`: Specify a branch (default: auto-detect the repository's default branch)
- `--output`: Specify a custom output filename (default is "combined_output.txt")

For example:
```bash
python github_downloader.py jonbrantingham github-repo-downloader --branch dev --output repo_contents.txt
```

## Output Format

The output file will contain all text files from the repository, with each file prefaced by a header showing the file path:

```
================================================================================
FILE: path/to/file.py
================================================================================

[file content here]


================================================================================
FILE: another/file.txt
================================================================================

[file content here]
```

## Error Handling

The script includes robust error handling:
- Automatically detects the repository's default branch
- If "main" branch is not found, it tries "master" branch
- Continues processing if a specific file or directory cannot be accessed
- Prints error messages for any issues encountered but keeps running

## Using with Claude Code

When using with Claude Code in your terminal, you can instruct it to execute this script for you. For example:

```
Download and run the github-repo-downloader project to download all files from a repository called 'example-repo' owned by 'example-user'
```

Claude Code can then:
1. Clone the repository
2. Install the necessary dependencies
3. Run the script with the parameters you specify

## Notes

- The GitHub API has rate limits for unauthenticated requests. For larger repositories, you might encounter rate limiting.
- Very large files might be skipped due to GitHub API limitations.
