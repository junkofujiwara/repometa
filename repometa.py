"""repometa.py"""
import os
import sys
from util.githubutil import GitHubUtil
def main():
    """main"""

    input_file = "data/list.csv"
    output_file = "data/metadata.csv"

    #get token from export commandline
    token = os.environ.get("GITHUB_TOKEN")
    if token is None:
        print("Please set GITHUB_TOKEN environment variable")
        sys.exit(1)

    # read list.csv file and insert into the list
    metadata = []
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().split("/")
            metadata.append(get_info(token, line[3], line[4]))

    # create csv file and insert metadata info
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("repo,star_count,fork_count,watch_count,"
                   "dependencies_count,contributors_count,dependents_count\n")
        for line in metadata:
            file.write(",".join(map(str, line)) + "\n")

def get_info(token, owner, repo):
    """get_info"""
    info = [f"{owner}/{repo}"]
    github_util = GitHubUtil(token, owner, repo)
    repo_details = github_util.get_repo_details()
    if repo_details is not None:
        info.append(repo_details.get("star_count"))
        info.append(repo_details.get("fork_count"))
        info.append(repo_details.get("watch_count"))
    else:
        info.append(None)
        info.append(None)
        info.append(None)
    info.append(github_util.get_dependencies_count())
    info.append(github_util.get_contributors_count())
    info.append(github_util.get_dependents_count())

    return info

if __name__ == "__main__":
    main()
