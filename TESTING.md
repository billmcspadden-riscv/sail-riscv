# Testing the RISCV-Sail model

This document contains information regarding the testing of the RISC-V
Sail model.

There are several goals for the testing effort of the RISC-V Sail model.
First, we need a set of tests that get run during the CI (Continuous Improvement)
cycle when merging PRs to the main branch.  We will refer to these as Build Verification Tests
(BVTs). These should cover basic instruction behavior.  The set of tests should run
rather quickly (perhaps 30 minutes) so that the CI does not bog down.

Second, we want to take Architectural Compatability Tests (ACTs) and run them
against the Sail model.  However, many of the ACTs are not self-checking and therefore
cannot be used directly for validating the functionality of the model.  But we can
run the Sail model and cross-check with the Spike model using signature checks.

Third,  for all of these test methods,  we want to be able to make coverage measurements
of the Sail code.  This will give us some objective insights into where we have coverage
holes in our testing.

## Background

For the longest time,  the set of tests used to validate changes to the
model,  were a set of precompiled .elf files (along with their .dump file counterparts)
that were stored in the repo under `test/riscv-tests`.  The scripts used to
run theses tests (and to gather test results) were `test/run_tests.sh` and
`test/run_fp_tests.sh`.

These tests are a compiled snapshot of tests that can be found at
https://github.com/riscv-software-src/riscv-tests
that date back to 2019.

This methodolgy was defecient in several ways.
1. Original test source is difficult to track down.
1. Storing compiled code in a git repo is usually frowned upon.
1. There is no easy way to add new tests to the repo when you add a new feature.
1. `run_tests.sh` is difficult to enhance with new features.

We anticipate that the `test/` directory will be removed once a more robust
testing methodolgy is put in place.  (See next section.)

## Adding new tests



To fix the defeciencies of the old test methodology,  we have done the
following:
1. Created a new test directory at the repo root, `TEST_DIR_ROOT/` under which
all new test collateral will be put.
1. Created a `bin/` directory under which various model scripts and executables
are added.
1. Installed https://github.com/riscv-software-src/riscv-tests as a subtree
at `TEST_DIR_ROOT/riscv-tests.git/`.  We will be working on  a special branch
in this repository: `riscv-tests-sail`.  This allows us to add tests onto our
branch.  And we can incorporate new tests into our testsuite as they appear
in the riscv-tests repo (by merging these new tests from the master branch
onto our branch).
1. Re-wrote `tests/run_tests.sh` in python and added run-time switches, the main
purpose of which was to be able to add command line switches to the execution of
particular tests. See the script, `bin/run_tests.py`, for execution parameters.
1. Updated `.github/workflows/compile.yml` to make use of the new run_tests python
script.



## Future Plans

### Sail and Spike Crosschecking with the Architecture Compatability Tests (ACTS)

We intend to run the ACTs on both Sail and Spike. Test signatures will be compared
to check that the two simulators agree.

### Fixing defecincies in the test environment

We have the following defeciencies in the test environment that need to be fixed:

1. A pass/fail can only be detected and reported from within the test itself.
If a test writer wanted to check the simluator log file to see
if certain strings existed (say, for example, you want to check the disassembly
of newly added instructions),  there is no method to do so.  The ability to
inspect the log file is a neccessary feature that needs to be added.

1. Negative testing. We need to be able to check for proper detection of errors
which would then mean that the test "passed".  For example,  we might want to check
that if the vector extension is not enabled, that a test that uses a vector instruction
would "fail".

1. Random test environment.  We would like to add a directed random test environment
that allows us to hit unforeseen boundary conditions.  We would like to randomize
both the instruction sequences as well as the model configuration.
