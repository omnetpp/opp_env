#!/usr/bin/env python3

import subprocess
import re
import datetime


def get_latest_tag():
    result = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get the latest tag: " + result.stderr)
    return result.stdout.strip()


def get_commits_since_tag(tag):
    result = subprocess.run(["git", "log", f"{tag}..HEAD", "--pretty=format:%s %H"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get commits: " + result.stderr)
    return [line.rsplit(' ', 1) for line in result.stdout.strip().splitlines()]


def get_files_changed(commit_hash):
    result = subprocess.run(["git", "show", "--name-only", "--pretty=format:", commit_hash], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get files changed: " + result.stderr)
    return result.stdout.strip().splitlines()


def categorize_commit(message, files_changed):
    if "opp_env/opp_env.py" in files_changed:
        return "opp_env"
    elif any(file.startswith("opp_env/") and file != "opp_env/opp_env.py" for file in files_changed):
        return "Database (Frameworks and Models)"
    return "Uncategorized"


def create_changelog(commits):
    changelog = "# Changes\n\n"
    version = f"x.y.z.{datetime.datetime.now():%y%m%d}"
    changelog += f"## {version}\n\n"

    categorized = {}
    for commit_message, commit_hash in commits:
        files_changed = get_files_changed(commit_hash)
        category = categorize_commit(commit_message, files_changed)
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(commit_message)

    for category, messages in categorized.items():        
        changelog += f"### {category}\n\n"
        for message in messages:
            if message.startswith("opp_env: "):
                message = message[len("opp_env:"):].strip()
            if message.startswith("external: "):
                message = message[len("external:"):].strip()
            if message.startswith("external.py: "):
                message = message[len("external.py:"):].strip()
            changelog += f"- {message}\n"
        changelog += "\n"

    return changelog


def main():
    try:
        latest_tag = get_latest_tag()
        commits = get_commits_since_tag(latest_tag)
        if not commits:
            print("No new commits since the last tagged version.")
            return
        
        changelog = create_changelog(commits)
        print(changelog)
    except RuntimeError as e:
        print(e)


if __name__ == "__main__":
    main()