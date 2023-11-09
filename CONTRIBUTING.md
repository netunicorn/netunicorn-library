# Contributing to netunicorn-library

Adapted from the IETF-tools/.github repository.

#### Table Of Contents

- [Rules](#rules)
  - [Python](#python)
  - [Git Commit Messages StyleGuide](#git-commit-messages-styleguide)
- [Workflow Overview](#contributing-workflow-overview)
- [Creating a Fork](#creating-a-fork)
- [Cloning a Fork](#cloning-a-fork)
- [Create a Local Branch](#create-a-local-branch)
- [Create and Push Commits](#create-and-push-commits)
- [Create a Pull Request](#create-a-pull-request)
- [Sync your Fork](#sync-your-fork)

## Rules

### Python

* Use folders `tasks` and `pipelines` for tasks and pipelines respectively. Choose (or create) a folder that best describes your task or pipeline.
* Don't re-format or modify code you're not working on (even to fit your preferred style).
* Adhere to PEP 8, the Style Guide for Python Code. Preferrably use Black style formatter to format your code.
* Do not modify `pyproject.toml` file in the repository. This would be modified by the lead developer when a new release is to be made.

### Git Commit Messages Styleguide

* Use the present tense ("Add task" not "Added tasks")
* Use the imperative mood ("Implement measurement..." not "Implements measurements for...")
* Limit the first line *(title)* to 72 characters or less
* Reference issues and pull requests liberally after the first line




## Contributing Workflow Overview

This project uses the **Git Feature Workflow** model.

It consists of a **main** branch which reflects the latest development state. New tasks and pipelines are added to this branch, until the version of the package in pyproject.toml is increased. At this point, the new release of netunicorn-library would be created and pushed to the PyPI repository.

A typical development workflow:

1. First, [create a fork](#creating-a-fork) of the repository and then [clone the fork](#cloning-a-fork) to your local machine.
2. [Create a new branch](#create-a-local-branch), based on the main branch, for the feature / task you are to work on.
3. [Add one or more commits and push them](#create-and-push-commits) to this branch.
4. [Create a pull request (PR)](#create-a-pull-request) to request your feature branch from your fork to be merged to the source repository `main` branch.
5. The PR is reviewed by the lead developer / other developers and the PR is merged with the `main` branch.
6. [Fast-forward (sync)](#sync-your-fork) your forked main branch to include the latest changes made by all developers.
7. Repeat this workflow from step 2.

![](https://github.com/ietf-tools/common/raw/main/assets/docs/workflow-diagram.jpg)

## Creating a Fork

As a general rule, work is never done directly on the project repository. You instead [create a fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) of the project. Creating a "fork" is producing a personal copy of the project. Forks act as a sort of bridge between the original repository and your personal copy.

1. Navigate to https://github.com/netunicorn/netunicorn-library
2. Click the **Fork** button. *You may be prompted to select where the fork should be created, in which case you should select your personal GitHub account.*

![](https://github.com/ietf-tools/common/raw/main/assets/docs/fork-button.jpg)

Your personal fork contains all the branches / contents of the original repository as it was at the exact moment you created the fork. You are free to create new branches or modify existing ones on your personal fork, as it won't affect the original repository.

Note that forks live on GitHub and not locally on your personal machine. To get a copy locally, we need to clone the fork...

## Cloning a Fork

Right now, you have a fork of the project repository, but you don't have the files in that repository locally on your computer.

After forking the project repository, you should have landed on your personal forked copy. If that's not the case, make sure you are on the fork (e.g. `john-doe/netunicorn-library` and not the original repository `netunicorn/netunicorn-library`).

Above the list of files, click the **Code** button. A clone dialog will appear.

![](https://github.com/ietf-tools/common/raw/main/assets/docs/code-button.png)

1. Copy the URL in the **Clone with SSL** dialog. 
2. In a terminal window, navigate to where you want to work. Subfolders will be created for each project you clone. **DO NOT** create empty folders for projects to be cloned. This is done automatically by git.
3. Type `git clone` and then paste the URL you just copied, e.g.:
```sh
git clone git@github.com:YOUR-USERNAME/netunicorn-library.git
```
4. Press **Enter**. Your local clone will be created in a subfolder named after the project.

## Create a Local Branch

While you could *technically* work directly on the main branch, it is best practice to create a branch for the tasks you are working on. It also makes it much easier to fast-forward your forks main branch to the match the source repository.

1. From a terminal window, nagivate to the project directory you cloned earlier.
2. First, make sure you are on the `main` branch.:
```sh
git checkout main
```
3. Let's create a branch named `my-tasks` based on the `main` branch:
```sh
git checkout -b my-tasks
```
4. Press **Enter**. A new branch will be created, being an exact copy of the main branch.

You are now ready to work on your features or tasks in your favorite editor.

## Create and Push Commits

While implementing your features or tasks, you will create one or more commits. A commit is a snapshot of your code at a specific point in time. It's a good practice to create small commits that are focused on a single task. This makes it easier to review and revert changes if necessary.

Push these commits to the remote branch (in our case, `my-tasks`) on your forked repository.
```sh
git push origin my-tasks
```

## Create a Pull Request

When your branch with tasks is ready to be merged with the source repository `main` branch, it's time to create a **Pull Request (PR)**.

On GitHub, navigate to your branch (in your forked repository). A yellow banner will invite you to **Compare & pull request**. You can also click the **Contribute** dropdown to initiate a PR.

![](https://github.com/ietf-tools/common/raw/main/assets/docs/pr-buttons.png)

Make sure the base repository is set to `netunicorn/netunicorn-library` with the branch `main` (this is the destination).

Enter a title and description of what your PR includes and click **Create pull request** when ready.

Your PR will then be reviewed by the lead developer / other developers.

Once approved and merged, your changes will appear in the `main` branch. It's now time to fast-forward your fork to the source repository. This ensures your fork main branch is in sync with the source main branch...

## Sync your Fork

Your fork `main` branch is now behind the source `main` branch. To fast-forward it to the latest changes, click the **Fetch upstream** button:

![](https://github.com/ietf-tools/common/raw/main/assets/docs/sync-branch.png)

Note that you also need to fast-forward your **local machine** `main` branch. This can again be done quickly from your editor / GUI tool. If you're using the command line, run these commands:

```sh
git checkout main
git pull
```
