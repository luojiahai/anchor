# Sheng Contributor's Guide

This is a guidance for how to report issues, propose new features, and submit contributions via Pull Requests (PRs).

---

## Before you start, file an issue

Please follow this simple rule to help me eliminate any unnecessary wasted effort and frustration, and ensure an efficient and effective use of everyone's time - yours, my, and other community members':

> 👉 If you have a question, think you have discovered an issue, would like to propose a new feature, etc., then find/file an issue **BEFORE** starting work to fix/implement it.

### File a new Issue

* Don't know whether you're reporting an issue or requesting a feature? File an issue
* Have a question that you don't see answered in docs, videos, etc.? File an issue
* Want to know if I'm planning on building a particular feature? File an issue
* Got a great idea for a new feature? File an issue/request/idea
* Don't understand how to do something? File an issue
* Found an existing issue that describes yours? Great - upvote and add additional commentary / info / repro-steps / etc.

### Complete the template

**Complete the information requested in the issue template, providing as much information as possible**. The more information you provide, the more likely your issue/ask will be understood and implemented.

---

## Development

### Fork, Clone, Branch and Create your PR

Once you have discussed your proposed feature/fix/etc. in the issue, it is time to start development:

1. Fork the repository if you have not already
2. Clone your fork locally
3. Create and push a feature branch
4. Create a [Draft Pull Request (PR)](https://github.blog/2019-02-14-introducing-draft-pull-requests/)
5. Work on your changes
6. Build and see if it works

### Testing

The testing module is in the `tst` folder which has:
* `data/input` folder: input files
* `data/expected` folder: expected output files

Please feel free to contribute testing:
* Create a `.zh` file with a meaningful file name in the `data/input` folder
* Write a Sheng program in the `.zh` file
* Create a `.out` file with the same file name as that of the first step in the `data/expected` folder
* Write the expected output ending with a newline (leave the last line blank) in the `.out` file

Run the following command with Python to execute all the tests:
```
python3 -m tst
```
The test results will be shown after the execution.

### Code Review

When you would like me to take a look, (even if the work is not yet fully-complete), mark the PR as 'Ready For Review' so that I can review your work and provide comments, suggestions, and request changes. It may take several cycles, but the end result will be solid, testable, conformant code that is safe for me to merge.

### Merge

Once your code has been reviewed and approved by me, it will be merged into the main branch. Once merged, your PR will be automatically closed.

---

## Thank you

Thank you in advance for your contribution\!
