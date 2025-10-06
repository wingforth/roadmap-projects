# Task Track

Task tracker is a project used to track and manage your tasks. A simple command line interface (CLI) is built to track what you need to do, what you have done, and what you are currently working on.

## Features

- Add a new task.
- Update a task description.
- Delete a task.
- Mark a task as in progress, done or todo.
- List all tasks.
- List tasks that are done, to done, in progress or todo.

## Required

- Python 3.8+
- git

## Install

Clone this repo with git:

```sh
git clone https://github.com/wingforth/roadmap-projects
cd roadmap-projects/task-tracker
```

## Usage

- Add a task:

  ```sh
  python task_tracker add <description>
  ```

- Update a task description:

  ```sh
  python task_tracker update <id> <description>
  ```

- Delete a task:

  ```sh
  python task_tracker delete <id>
  ```

- Mark a task on a status (todo, in-progress, done):

  ```sh
  python task_tracker mark <id> <status>
  ```

- List all task:

  ```sh
  python task_tracker list
  ```

- List task that on a status (todo, in-progress, done, not-done):

  ```sh
  python task_tracker list <status>
  ```
