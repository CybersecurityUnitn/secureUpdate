# Secure Update 

This repository contains all the implementation and test material used in our
proposal for an extended version of the SUIT (Software Updates for Internet of
Things) standard. In particular, it includes a fork and extension of the
`suit-tool` reference implementation, developed by ARM (available at:
https://gitlab.arm.com/research/ietf-suit/suit-tool) and a fork and extension
of `suit-parser`, also developed by ARM (available at
https://gitlab.arm.com/research/ietf-suit/suit-parser). 

## Contents of the repo

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
    - a script (`make-examples.sh`) to automate the generation, signing and
      parsing of the manifests;
    - in the `SBOM` folder, a set of three sample Software Bill Of Materials
      of various sizes;
    - in the `manifests` folder, a set of ten sample manifests used for the
      experimental evaluation of the implementation;
    - in the `proofs` folder, a set of proofs of various formal properties
      together with a script (`make_proofs.sh`) to automate and time the proof
      verification process.
- The `test_results` folder contains the results of parsing and validating the
  sample manifests on a Raspberry Pi 4B (quad-core ARM Cortex-A72 processor
  running at 1.5 GHz with 2 GB of RAM).
