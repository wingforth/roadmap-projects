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

- python 3.8+
- git

## Install

Clone this repo with git:

```sh
git clone https://github.com/wingforth/roadmap-projects
cd roadmap-projects/task-tracker-2
```

## Usage

1. First start task-tracker:

   ```sh
   python -m task_tracker
   ```

2. Than you can take following action on tasks.

   - Add a task:

     ```sh
     add <description>
     ```

   - Update a task description:

     ```sh
     update <id> <description>
     ```

   - Delete a task:

     ```sh
     delete <id>
     ```

   - Mark a task on a status (todo, in-progress, done):

     ```sh
     mark <id> <status>
     ```

   - List all task:

     ```sh
     list
     ```

   - List task that on a status (todo, in-progress, done, not-done):

     ```sh
     list <status>
     ```

3. At last exit task-tracker:

   ```sh
   exit
   ```

   Or enter **end-of-file** (EOF) by pressing **Ctrl-D** (Unix or Linux) or **Ctrl-Z** (Windows).
