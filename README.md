# Merge-test Docker Action

Tests whether commits can be [cherry-picked](https://git-scm.com/docs/git-cherry-pick) into a target branch.
Originally this is for checking of commits from a pull request can be "merged" into other branches
than their destination branch, e.g. release branches.

The action fails if any of the used commands fail and the pseudo-code is something along the following lines:

```
git clone --branch $TARGET_BRANCH https://github.com/$TARGET_REMOTE.git
git cherry-pick $SOURCE_COMMITS
```
