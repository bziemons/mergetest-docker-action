#!/usr/bin/env python3

import os
import pathlib
import sys

import sh
from sh import git


def input_name(name: str):
    return f"INPUT_{name.upper()}"


def get_input(name: str):
    """Basically does the same as https://github.com/actions/toolkit/blob/master/packages/core/src/core.ts#L60-L75"""
    if input_name(name) in os.environ:
        return os.environ.get(input_name(name))
    else:
        raise RuntimeError(f"Cannot find environment variable for {name}")


def get_github_url():
    return os.environ.get('GITHUB_URL', default='https://github.com')


def add_or_set_git_remote(remote_name, remote_uri):
    if remote_name in str(git.remote()).splitlines(keepends=False):
        git.remote("set-url", remote_name, remote_uri)
    else:
        git.remote.add(remote_name, remote_uri)


def set_git_author_info(name: str, email: str):
    git.config("user.name", name)
    git.config("user.email", email)


def main():
    github_remote_url = f"{get_github_url()}/{get_input('target_remote')}.git"
    work_dir = pathlib.Path(get_input("work_dir"))
    if work_dir.is_dir() and len(list(work_dir.iterdir())) > 0:
        os.chdir(work_dir)
        remote = "origin"
        if get_input("source_remote_name") == remote:
            remote = remote + "2"
        add_or_set_git_remote(remote, github_remote_url)
        git.fetch(remote)
        git.checkout("-B", get_input("target_branch"), f"{remote}/{get_input('target_branch')}")
        git.reset("--hard", "HEAD")
        git.clean("-fdx")
    else:
        git.clone("--branch", get_input("target_branch"), github_remote_url, str(work_dir))
        os.chdir(work_dir)

    if get_input("target_remote") != get_input("source_remote"):
        source_remote_name = get_input("source_remote_name")
        add_or_set_git_remote(source_remote_name, f"{get_github_url()}/{get_input('source_remote')}.git")
        git.fetch(source_remote_name)

    set_git_author_info(f"GitHub Action {os.environ['GITHUB_ACTION']}", "action@localhost")

    try:
        git("cherry-pick", get_input("source_commits"))
        print("Source commits were cherry-picked successfully", file=sys.stderr)
    except sh.ErrorReturnCode:
        print("Source commits could not be cherry-picked", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
