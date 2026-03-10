# Repository Guidelines

## Project Structure & Module Organization
`Codex_example/` is currently minimal and only contains top-level documentation. `README.md` is empty today, so contributors should keep this guide accurate as the example grows. Place runtime code in `src/`, automated tests in `tests/`, and sample inputs or fixtures in `assets/` or `fixtures/`. Keep modules focused and name files by responsibility, for example `src/task_runner.py` and `tests/test_task_runner.py`.

## Build, Test, and Development Commands
No project-specific build, run, or test toolchain is configured in this directory yet. Until one is added, use lightweight repository checks:

- `rg --files .` lists files quickly.
- `git status --short -- Codex_example` shows changes limited to this example.
- `git log --oneline -- Codex_example` reviews history for this directory.

If your change introduces a language runtime or framework, add the exact setup, run, and test commands to `README.md` in the same change.

## Coding Style & Naming Conventions
Use descriptive, lowercase paths and keep filenames ASCII unless there is a strong reason not to. Follow language-standard naming: `snake_case` for files and functions, `PascalCase` for classes, and short imperative headings in Markdown. Prefer small modules over large multi-purpose files. Use the formatter and linter that match the language you introduce, and document them immediately once adopted.

## Testing Guidelines
There are no automated tests in this directory yet. New features should add a repeatable test suite under `tests/` and keep test names aligned with the implementation module. If automated coverage is not practical, include manual verification steps in the pull request, with exact commands and expected results.

## Commit & Pull Request Guidelines
Recent history mixes plain imperative subjects with Conventional Commit prefixes such as `feat:`. Prefer the Conventional Commit style (`feat:`, `fix:`, `docs:`) because it is easier to scan and filter. Keep each commit focused on one logical change. Pull requests should include a short summary, the files or paths changed, verification steps, and any follow-up work. Add screenshots only when a UI or rendered output changes.

## Scope & Isolation
Treat `Codex_example/` as a self-contained example inside a larger workspace. Avoid editing sibling example folders unless the task explicitly requires coordinated changes.

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.

How to use skills:
Unified skill cli. If you are not sure, you can first use "magicskills listskill" to search for available skills. Then, determine which skill might be the most useful. After that, try to use "magicskills readskill <path>" to read the SKILL.md file under this skill path to get more detailed information. Finally, based on the content of this file, decide whether to read the documentation in other paths or use "magicskills execskill <command>" to directly execute the relevant script.

</usage>

<!-- SKILLS_TABLE_END -->

</skills_system>
