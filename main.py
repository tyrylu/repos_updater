import os
from datetime import datetime, timedelta, timezone
import locale
import pygit2
from pygit2 import GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from jinja2 import Environment, FileSystemLoader
import click
import git_utils
from git_utils import PullResult


def commit_time_str(commit):
    commit_time = datetime.fromtimestamp(commit.commit_time, timezone(timedelta(hours=commit.commit_time_offset/60)))
    return commit_time.strftime("%c %z")

def signature_time_str(signature):
    time = datetime.fromtimestamp(signature.time, timezone(timedelta(hours=signature.offset/60)))
    return time.strftime("%c %z")

def commit_is_interesting(commit):
    no_interesting_prefixes = ["Merge ", "Bump ", "[tx-robot]", "Merge!", "Land #", "Auto merge", "Update dependency", "Update Rust crate", "Rollup merge", "build(deps)", "automatic module_metadata_base.json update", "Autosync the updated", "Localisation update", "Translated using", "chore(deps)"]
    for prefix in no_interesting_prefixes:
        if commit.message.startswith(prefix):
            return False
    if commit.message.startswith("Update") and commit.message.strip().endswith("translation"):
        return False
    return True

def generate_changelog(repo, old_head):
    commits = []
    interesting_commits = 0
    for commit in repo.walk(repo.head.target, GIT_SORT_TIME|GIT_SORT_TOPOLOGICAL):
        if commit.oid == old_head:
            break
        is_interesting = commit_is_interesting(commit)
        if is_interesting:
            interesting_commits += 1
        commits.append((commit, is_interesting))
    generate = True
    if interesting_commits < 1:
        generate = False
    repo_name = repo.path.split("/")[-3]
    if interesting_commits > 50:
        generate = click.confirm(f"\aAbout to generate a changelog for {interesting_commits} interesting commits out of a total of {len(commits)} of repository {repo_name}. Continue?")
    if generate:
        print("Generating changelog...")
        tpl = env.get_template("commits_report.tpl")
        rendered = tpl.render(commits=reversed(commits), num_commits=len(commits))
        os.makedirs("changelogs", exist_ok=True)
        dest = os.path.join("changelogs", f"{repo_name} ({interesting_commits} of {len(commits)}).htm")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(rendered)

def update_repo(path):
    try:
        repo = pygit2.Repository(path)
    except pygit2.GitError:
        print(f"Can not update {path}, either it is not a vcs controlled project or the vcs is not supported.")
        return
    old_head = repo.head.target
    res = git_utils.pull(repo)
    if res is PullResult.merged or res is PullResult.fast_forwarded:
        generate_changelog(repo, old_head)
    return res

locale.setlocale(locale.LC_ALL, "")
env = Environment(loader=FileSystemLoader(searchpath=os.path.dirname(__file__)), trim_blocks=True, lstrip_blocks=True)
env.globals["commit_time_str"] = commit_time_str
env.globals["signature_time_str"] = signature_time_str
root = input("Enter the repositories container path: ")
results = {}
for entry in os.listdir(root):
    path = os.path.join(root, entry)
    if os.path.isdir(path):
        print(f"Processing repository {entry}...")
        res = update_repo(path)
        if not res: continue
        if res not in results:
            results[res] = []
        results[res].append(path)
ok_results = {PullResult.up_to_date, PullResult.fast_forwarded, PullResult.merged}
for res, repos in results.items():
    if res not in ok_results:
        print(f"{len(repos)} was {res.name}: {repos}")
    else:
        print(f"{len(repos)} was {res.name}")
input("Done.")