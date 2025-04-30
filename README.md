# Secure Update 

This repository contains all the implementation and test material used to propose an extended version of SUIT (Software Updates for Internet of Things). In particular, it includes a fork and extension of the suit-tool reference implementation, developed by ARM (available at: https://gitlab.arm.com/research/ietf-suit/suit-tool) and a fork and extension of the suit-parser, also developed by ARM (available at https://gitlab.arm.com/research/ietf-suit/suit-parser).

## Content of the repo
The repository is organized as follows.

- The `SUIT-Tool` folder contains the codebase of the Python tool to generate
  and parse the extended manifests.
- The `SUIT-Parser` folder contains the codebase of the C tool to parse and
  validate the extended manifests.
- The `optee_examples` folder contains a copy of the OpTEE sample applications
  repo (cloned from https://github.com/linaro-swg/optee_examples) with the
  modified versions used to build the proof certificates for the control flow
  properties.
- The `examples` folder contains:
    - a set of manifest examples (used for testing) with scripts to automate the generation, signing and parsing of the manifests in the folder;
    - a set of proofs of various properties used for testing with scripts to automate the proof verification.
- The `test_results` folder contains the results of parsing and validating the
  sample manifests on a Raspberry Pi 4B (quad-core ARM Cortex-A72 processor
  running at 1.5 GHz with 2 GB of RAM).
