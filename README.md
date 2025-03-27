# Secure Update 

This repository contains all the implementation and test material used to propose an extended version of SUIT (Software Updates for Internet of Things). In particular, it includes a fork and extension of the suit-tool reference implementation, developed by ARM (available at: https://gitlab.arm.com/research/ietf-suit/suit-tool) and a fork and extension of the suit-parser, also developed by ARM (available at https://gitlab.arm.com/research/ietf-suit/suit-parser).

## Content of the repo
The repository is organized as follows:

- the example folder contains:
    - a set of manifest examples (used for testing) with scripts to automate the generation, signing and parsing of the manifests in the folder;
    - a set of proofs of various properties used for testing with scripts to automate the proof verification.
- the SUIT-Parser folder contains the codebase of the tool to parse the manifests in C;
- the SUIT-Tool folder contains the codebase of the tool to generate and parse the manifests in Python;
- the tests folder contains the result of example tested on a Raspberry Pi 4b (quad-core ARM Cortex-A72 processor running at 1.5 GHz and 2 GB of RAM).