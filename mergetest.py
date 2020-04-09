#!/usr/bin/env python3

import os
import pathlib
import sys

import sh
from sh import git


def input_name(name: str):
    return f"INPUT_{name.upper()}"


def input_exists(name: str):
    return input_name(name) in os.environ


def get_input(name: str):
    """Basically does the same as https://github.com/actions/toolkit/blob/master/packages/core/src/core.ts#L60-L75"""
    if input_exists(name):
        return os.environ.get(input_name(name))
    else:
        raise RuntimeError(f"Cannot find environment variable for {name}")


def get_github_url():
    return os.environ.get('GITHUB_URL', default='https://github.com')


def get_git_authentication_key():
    return f"http.{get_github_url()}/.extraheader"


def configure_git_authentication():
    def auth_token(token: str):
        return f"AUTHORIZATION: basic {token}"

    git.config("--global", get_git_authentication_key(), auth_token("***"))
    # avoids using the token in a shell argument, which might end up in audit logs
    with open(os.path.join(os.environ.get('HOME'), ".gitconfig"), "r+") as fhandle:
        readlines = fhandle.readlines()
        fhandle.seek(0)
        for line in readlines:
            fhandle.write(line.replace(auth_token("***"), auth_token(get_input("token"))))


def add_or_set_git_remote(remote_name, remote_uri):
    if remote_name in str(git.remote()).splitlines(keepends=False):
        git.remote("set-url", remote_name, remote_uri)
    else:
        git.remote.add(remote_name, remote_uri)


def main():
    set_token = input_exists("token")
    if set_token:
        configure_git_authentication()
    try:
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
        try:
            git("cherry-pick", get_input("source_commits"))
            print("Source commits were cherry-picked successfully", file=sys.stderr)
        except sh.ErrorReturnCode:
            print("Source commits could not be cherry-picked", file=sys.stderr)
            raise
    finally:
        if set_token:
            # it is safer to remove the authentication token
            git.config("--global", "--unset-all", get_git_authentication_key())


if __name__ == "__main__":
    main()
