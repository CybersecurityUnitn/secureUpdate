# SUIT TOOL EXTENSION

This is a fork and an extension of the suit-tool reference implementation, developed by ARM, and available at: https://gitlab.arm.com/research/ietf-suit/suit-tool. 

# Content of the repo

This repository contains suit-tool, a tool to generate and sign manifests following the SUIT specification (https://tools.ietf.org/html/draft-ietf-suit-manifest-14). It also includes the possibility to parse the manifest into human-readable format (JSON and SUIT-debug) and verify the manifest signature. 

The repository is organized as follows:
* the `bin` folder contains the files needed to install the tool and a small example to test the basic functionalities;
* the `example` folder contains a set of examples used for testing and a script to generate, sign and parse the manifests of the examples in the folder. It also includes some SBOMs used in the examples;
* the `suit-tool` folder contains the actual codebase of the tool;
* the `tests` folder contains the result of the tested example on a Raspberry Pi 4b (quad-core ARM Cortex-A72 processor running at 1.5 GHz and 2 GB of RAM). 

# Installing

## For usage only

First clone this repo:

```
$ git clone https://github.com/CybersecurityUnitn/secureUpdate.git
```

Next, use pip to install the repo:

```
$ cd suit-manifest-generator
$ python3 -m pip install --user --upgrade .
```

## For development 

To setup the development enviroment, first clone this repo: 

```
$ git clone https://github.com/CybersecurityUnitn/secureUpdate.git
$ cd secureUpdate
```

Next, create a Python virtual enviroment:

```
$ python3 -m venv myenv
```

Activate the virtual enviroment:

```
$ source myenv/bin/activate
```

Install the tool package in editable mode to be able to modify the source code and apply the changes without reinstalling reinstalling it.

```
$ pip install --editable .
```

Verify the installation:

```
suit-tool --help
```

To uninstall the suit-tool package, use:

```
pip uninstall ietf-suit-tool
```

Followed by `y` or `yes` as confirmation.  


# Input File Description

The input file is organised into several high-level elements:

* `manifest-version` (a positive integer), the version of the manifest specification
* `manifest-sequence-number` (a positive integer), the anti-rollback counter of the manifest
* `components`, a list of components that are described by the manifest
* `certification-manifest`, a list of proof descriptors that verify the update package
* `software-bill-of-materials`, a severable element containing the BOM of the components in the update package 


## Component

Each component is a JSON map that may contain the following elements. Some elements are required for the target to be able to install the component.

Required elements:

* `install-id` (a Component ID), the identifier of the location to install the described component.
* `install-digest` (a SUIT Digest), the digest of the component after installation.
* `install-size` (a positive integer), the size of the component after installation.
* `vendor-id` (a RFC 4122 UUID), the UUID for the component vendor. This must match the UUID that the manifest processor expects for the specified `install-id`. The suit-tool expects at least one component to have a `vendor-id`
* `class-id` (a RFC 4122 UUID), the UUID for the component. This must match the UUID that the manifest processor expects for the specified `install-id`. The `suit-tool` expects at least one component with a `vendor-id` to also have a `class-id`
* `file` (a string), the path to a payload file. The `install-digest` and `install-size` will be calculated from this file.

Some elements are not required by the tool, but are necessary in order to accomplish one or more use-cases.

Optional elements:

* `bootable` (a boolean, default: `false`), when set to true, the `suit-tool` will generate commands to execute the component, either from `install-id` or from `load-id` (see below)
* `uri` (a text string), the location at which to find the payload. This element is required in order to generate the `payload-fetch` and `install` sections.
* `loadable` (a boolean, default: `false`), when set to true, the `suit-tool` loads this component in the `load` section.
* `compression-info` (a choice of string values), indicates how a payload is compressed. When specified, payload is decompressed before installation. The `install-size` must match the decompressed size of the payload and the install-digest must match the decompressed payload. N.B. The suit-tool does not perform compression. Supported values are:

    * `zlib`
    * `bzip2`
    * `deflate`
    * `lz4`
    * `lzma`

* `download-digest` (a SUIT Digest), a digest of the component after download. Only required if `compression-info` is present and `decompress-on-load` is `false`.
* `decompress-on-load` (a boolean, default: `false`), when set to true, payload is not decompressed during installation. Instead, the payload is decompressed during loading. This element has no effect if `loadable` is `false`.
* `load-digest` (a SUIT Digest), a digest of the component after loading. Only required if `decompress-on-load` is `true`.
* `install-on-download` (boolean, default: true), If true, payload is written to `install-id` during download, otherwise, payload is written to `download-id`.
* `download-id` (a component id), the location where a downloaded payload should be stored before installation--only used when `install-on-download` is `false`.

### Component ID

The `suit-tool` expects component IDs to be a JSON list of strings. The `suit-tool` converts the strings to bytes by:

1. Attempting to convert from hex
2. Attempting to convert from base64
3. Encoding the string to UTF-8

For example,

* `["00"]` will encode to `814100` (`[h'00']`)
* `["0"]` will encode to `814130` (`[h'30']`)
* `["MTIzNA=="]` will encode to `814431323334` (`[h'31323334']`)
* `["example"]` will encode to `81476578616D706C65` (`[h'6578616d706c65']`)

N.B. Be careful that certain strings can appear to be hex or base64 and will be treated as such. Any characters outside the set `[0-9a-fA-F]` ensure that the string is not treated as hex. Any characters outside the set `[0-9A-Za-z+/]` or a number of characters not divisible by 4 will ensure that the string is not treated as base64.

## Certification manifest

The certification manifest is a JSON map that contains one or more proof descriptors. Each of them has a fixed structure containing the following fields:
* `property identifier`, which is used to uniquely identify the formal property that the proof descriptor refers to
* `component identifiers`, a list used to select which components are targeted by the considered proof (must match one or more component IDs)
* `language identifier`, which is used to specify the formal language in which the proof is expressed
* `proof certificate`, expressed in the formal language singled out by the language identifier (the encoding can be decided according to the capabilities of the parser)
* `locality constraint`, which is a boolean flag whose setting requires the proof verification step to be performed on the device, without involving any communication with the external world
* `verification servers`, a list of URI of external servers which can be queried to perform the verification of the associated proof certificate (considered only when the locality constraint flag is not set)

## Software bill of materials

The SBOM is a severable element representing the Software Bill of Material, which describes the components contained in the update. It can contain different kinds of information, such as the component provider, the dependency, the vulnerabilities, etc. 

Examples of SBOM can be found in the `examples` subfolder. They comply with the CycloneDX standard, have a JSON format and are included in the manifests used as examples after minimization and encoding in Base64. 

## SUIT Digest

The format of a digest is a JSON map:

```JSON
{
    "algorithm-id" : "sha256",
    "digest-bytes" : "base64-or-hex"
}
```

The `algorithm-id` must be one of:

* `sha224`
* `sha256`
* `sha384`
* `sha512`

The `digest-bytes` is a string of either hex- or base64-encoded bytes. The same decoding rules as those in Component ID are applied.

## Example Input File

```JSON
{
    "components" : [
        {
            "install-id" : ["00"],
            "install-digest": {
                "algorithm-id": "sha256",
                "digest-bytes": "00112233445566778899aabbccddeeff0123456789abcdeffedcba9876543210"
            },
            "install-size" : 34768,
            "uri": "http://example.com/file1.bin",
            "vendor-id" : "fa6b4a53-d5ad-5fdf-be9d-e663e4d41ffe",
            "class-id" : "1492af14-2569-5e48-bf42-9b2d51f2ab45",
            "bootable" : true
        },
        {
            "install-id" : ["01"],
            "install-digest": {
                "algorithm-id": "sha256",
                "digest-bytes": "0123456789abcdeffedcba987654321000112233445566778899aabbccddeeff"
            },
            "install-size" : 76834,
            "uri": "http://example.com/file2.bin"
        }
    ],
    "certification-manifest": [
        {
            "property-id": "123e4567-e89b-12d3-a456-426655447770",
            "language-id": "cpc",
            "component-id": ["00"],
            "proof-certificate": "00100000000000000000000000111111111...11111111111111100000000000000000000000000000000000000000",
            "locality-constraint": true,
            "verification-servers": []
        },
        {
            "property-id": "987e6543-e21b-12d3-a456-426655440000",
            "language-id": "cpc",
            "component-id": ["00"],
            "proof-certificate": "001000000000101010101010...101011111111111",
            "locality-constraint": false,
            "verification-servers": [
                {
                    "uri": "http://example.com/verify"
                },
                {
                    "uri": "http://example.com/verify2"
                }
            ]
        },
        {
            "property-id": "1492af14-2569-5e48-bf42-9b2d51f2ab45",
            "language-id": "cpc",
            "component-id": ["01"],
            "proof-certificate": "001000000000101010....1010101010111111111110000000000000000000000000000",
            "locality-constraint": false,
            "verification-servers": [
                {
                    "uri": "http://example.com/component2/verify"
                }
            ]
        }

    ],
    "manifest-version": 1,
    "manifest-sequence-number": 5,
    "severable": true,
    "manifest-description": "This is a (severable) description of the manifest.",
    "software-bill-of-materials": "{'$schema':'http://cyclonedx.org/schema/bom-1.6.schema.json','bomFormat':'CycloneDX','specVersion':'1.6','serialNumber':'urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79','version':1,'metadata':{'timestamp':'2024-11-08T09:58:11+00:00'},'components':[{'type':'firmware','name':'Baremetal-TEE-MPU-version','version':'1.0','description':'A Baremetal TEE for devices with Memory Protection Unit (MPU) supporting GlobalPlatform TEE APIs','licenses':[{'license':{'id':'Apache-2.0'}}],'externalReferences':[{'type':'website','url':'https://github.com/crosscon/baremetal-tee/blob/main/MPU-version/README.md'},{'type':'vcs','url':'git@github.com:crosscon/baremetal-tee.git'}]},{'type':'library','name':'Mbed TLS','version':'3.6.0','description':'An open source, portable, easy to use, readable and flexible TLS library, and reference implementation of the PSA Cryptography API.','hashes':[{'alg':'SHA-256','content':'3ecf94fcfdaacafb757786a01b7538a61750ebd85c4b024f56ff8ba1490fcd38'}],'licenses':[{'license':{'id':'Apache-2.0'}}],'externalReferences':[{'type':'website','url':'https://www.trustedfirmware.org/projects/mbed-tls'},{'type':'issue-tracker','url':'https://github.com/Mbed-TLS/mbedtls/issues'},{'type':'vcs','url':'git@github.com:Mbed-TLS/mbedtls.git'}]}]}]}"
}

```

# Invoking the suit-tool

The `suit-tool` supports three sub-commands:

* `create` generates a new manifest.
* `sign` signs a manifest.
* `parse` parses an existing manifest into cbor-debug or a json representation.
* `keygen` create a signing key. Not for production use.
* `pubkey` get the public key for a supplied private key in uECC-compatible C definition.
* `verify` verify the signature of the manifest. 

The `suit-tool` has a configurable log level, specified with `-l`:

* `suit-tool -l debug` verbose output
* `suit-tool -l info` normal output
* `suit-tool -l warning` suppress informational messages
* `suit-tool -l exception` suppress warning and informational messages

## Create

To create a manifest, invoke the `suit-tool` with:

```sh
suit-tool create -i IFILE -o OFILE
```

The format of `IFILE` is as described above. `OFILE` defaults to a CBOR-encoded SUIT manifest.

`-f` specifies the output format:

* `suit`: CBOR-encoded SUIT manifest
* `suit-debug`: CBOR-debug SUIT manifest
* `json`: JSON-representation of a SUIT manifest

The `suit-tool` can generate a manifest with severable fields. To enable this mode, add the `-s` flag.

To add a component to the manifest from the command-line, use the following syntax:

```
-c 'FIELD1=VALUE1,FIELD2=VALUE2'
```

The supported fields are:

* `file` the path fo a file to use as a payload file.
* `inst` the `install-id`.
* `uri` the URI where the file will be found.

## Sign

To sign an existing manifest, invoke the `suit-tool` with:

```sh
suit-tool sign -m MANIFEST -k PRIVKEY -o OFILE
```

`PRIVKEY` must be a secp256r1 ECC private key in PEM format.

If the COSE Signature needs to indicate the key ID, add a key id with:

```
-i KEYID
```

## Parse

To parse an existing manifest, invoke the `suit-tool` with:

```sh
suit-tool parse -m MANIFEST
```

If a json-representation is needed, add the '-j' flag.

## Keygen

Create an asymmetric keypair for non-production use. Production systems should use closely guarded keys, such as keys stored in an HSM.

```sh
 suit-tool keygen [-t TYPE] -o KEYFILE
 ```

`suit-tool keygen` defaults to creating SECP256r1 keys. To create another type of key, use `-t`followed by one of:

* `secp256r1`
* `secp384r1`
* `secp521r1`
* `ed25519`

## UECC public key

Derive a public key in the format used by micro ECC. The input is a PEM private key.

```sh
suit-tool pubkey -k FILE
```

The tool will then print the public key in micro ECC format. To write the key into a file use '-o' followed by the name of the file. 

## Signature verification 

To verify the signature of a manifest, invoke the `suit-tool` with:

```sh
suit-tool verify -k FILE -s SIGNED-MANIFEST 
```

The algorithm used to create the signature of the manifest should be one of the following:
* `secp256r1`
* `secp384r1`
* `secp521r1`
* `ed25519`

The result of the verification is printed on the console (or in the file that is passed as output). 