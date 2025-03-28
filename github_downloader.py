import os
import requests
from urllib.parse import urljoin
import base64
import argparse
import json

def get_default_branch(owner, repo):
    """Get the default branch name for a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    response.raise_for_status()
    repo_info = response.json()
    return repo_info.get("default_branch", "main")

def get_repo_contents(owner, repo, path="", branch=None):
    """Get contents of a repository directory or file."""
    # If branch is not specified, use the default branch
    if branch is None:
        branch = get_default_branch(owner, repo)
        print(f"Using default branch: {branch}")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404 and branch == "main":
            # If 404 with main branch, try master
            print("Branch 'main' not found. Trying 'master' branch...")
            params = {"ref": "master"}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        else:
            # Re-raise the exception if it's not a 404 for main branch
            raise

def download_files(owner, repo, branch=None, output_file="combined_output.txt"):
    """
    Download all files from a repository and combine them into a single text file.
    """
    # Create output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Start recursive download from root
        download_directory(owner, repo, "", branch, outfile)
    
    print(f"All files downloaded and combined into {output_file}")

def download_directory(owner, repo, path, branch, outfile):
    """
    Recursively download all files from a directory and append them to the output file.
    """
    try:
        contents = get_repo_contents(owner, repo, path, branch)
        
        # Handle case when content is a list (directory)
        if isinstance(contents, list):
            for item in contents:
                if item["type"] == "file":
                    # Skip binary files and other non-text formats
                    _, ext = os.path.splitext(item["name"])
                    if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', 
                                      '.gz', '.exe', '.bin', '.mp3', '.mp4', '.avi']:
                        print(f"Skipping binary file: {item['path']}")
                        continue
                        
                    # Download and append text file
                    download_and_append_file(item, outfile, owner, repo, branch)
                elif item["type"] == "dir":
                    # Recursively download subdirectory
                    download_directory(owner, repo, item["path"], branch, outfile)
        else:
            # Handle case when content is a single file
            download_and_append_file(contents, outfile, owner, repo, branch)
    except Exception as e:
        print(f"Error accessing directory {path}: {str(e)}")

def download_and_append_file(file_item, outfile, owner, repo, branch):
    """
    Download a single file and append it to the output file.
    """
    try:
        # First attempt to use content if it's available in the API response
        if "content" in file_item and file_item.get("encoding") == "base64":
            content = base64.b64decode(file_item["content"]).decode('utf-8', errors='replace')
        else:
            # For files that are too large or don't have content/encoding in the API response
            if "download_url" in file_item and file_item["download_url"]:
                response = requests.get(file_item["download_url"])
                response.raise_for_status()
                content = response.text
            else:
                # If there's no download URL, try getting the direct raw URL
                # Use the correct branch
                if branch is None:
                    branch = get_default_branch(owner, repo)
                
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_item['path']}"
                response = requests.get(raw_url)
                response.raise_for_status()
                content = response.text
        
        # Write file path and content to output
        outfile.write(f"\n\n{'=' * 80}\n")
        outfile.write(f"FILE: {file_item['path']}\n")
        outfile.write(f"{'=' * 80}\n\n")
        outfile.write(content)
        print(f"Added: {file_item['path']}")
    except Exception as e:
        print(f"Error processing file {file_item['path']}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and combine all files from a GitHub repository")
    parser.add_argument("owner", help="Repository owner (username or organization)")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("--branch", default=None, help="Branch name (default: auto-detect repository default branch)")
    parser.add_argument("--output", default="combined_output.txt", help="Output filename")
    
    args = parser.parse_args()
    
    download_files(args.owner, args.repo, args.branch, args.output)
