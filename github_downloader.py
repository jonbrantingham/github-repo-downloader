import os
import requests
from urllib.parse import urljoin
import base64
import argparse

def get_repo_contents(owner, repo, path="", branch="main"):
    """Get contents of a repository directory or file."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def download_files(owner, repo, branch="main", output_file="combined_output.txt"):
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
                download_and_append_file(item, outfile)
            elif item["type"] == "dir":
                # Recursively download subdirectory
                download_directory(owner, repo, item["path"], branch, outfile)
    else:
        # Handle case when content is a single file
        download_and_append_file(contents, outfile)

def download_and_append_file(file_item, outfile):
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
                raw_url = f"https://raw.githubusercontent.com/{file_item['url'].split('repos/')[1].split('/contents/')[0]}/main/{file_item['path']}"
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
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    parser.add_argument("--output", default="combined_output.txt", help="Output filename")
    
    args = parser.parse_args()
    
    download_files(args.owner, args.repo, args.branch, args.output)
