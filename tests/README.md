# Test results 
    
- Example 1: Single component, 2 proof inside the manifest encoded in Base64:
        1. Proof name: 'hello01iso.cpc' with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'pic32mz2.cpc' with original size of 40.8kB, compressed 6.6kB. 
        SBOM: 2.4 kB
        Total size: 123.5 kB
        Parsing & signature: 0.09 s, 6144 kB
        Proofs verification: 1.98 + 0.39 = 2.37 s, 80384 kB

- Example 2: Single component, 3 proof inside the manifest encoded in Base64:
        1. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'hello01p.cpc', with original size of 476.2kB, compressed 72.0 kB.
        2. Proof name: 'pic32mz2.cpc' with original size of 40.8kB, compressed 6.6kB. 
        SBOM: 2.4 kB
        Total size: 219.7 kB
        Parsing & signature: 0.08 s, 6656 kB
        Proofs verification: 1.98 + 1.65 + 0.39 = 4.02 s, 80384 kB
        
- Example 3: Double components, 4 proof inside the manifest encoded in Base64
        1. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'hello01p.cpc', with original size of 476.2kB, compressed 72.0 kB.
        3. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        4. Proof name: 'mempart.cpc' with original size of 15.3 kB, compressed 2.7kB.
        SBOM: 34.7 kB
        Total size: 3.1 MB
        Parsing & signature: 0.59 s, 18432 kB
        Proofs verification: 1.98 + 1.65 + 85.49 + 0.29 = 89.41, 1318912 kB

- Example 4: Double component, 4 proof inside the manifest encoded in Base64
        1. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        3. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        4. Proof name: 'mempart.cpc' with original size of 15.3 kB, compressed 2.7 kB. 
        SBOM: 34.7 kB
        Total size: 6.1 MB
        Parsing & signature: 1.05 s, 30208 kB
        Proofs verification: 1.98 + 97.41 + 85.49 + 0.29 = 185.17 s, 1657856 kB

- Example 5: Double component, 5 proof inside the manifest encoded in Base64
        1. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'hello01p.cpc', with original size of 476.2kB, compressed 72.0 kB.
        3. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        4. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        5. Proof name: 'mempart.cpc' with original size of 15.3 kB, compressed 2.7 kB. 
        6. Proof name: 'pic32mz2.cpc' with original size of 40.8kB, compressed 6.6kB.
        SBOM: 34.7 kB
        Total size: 6.2 MB 
        Parsing & signature: 1.11 s, 30208 kB
        Proofs verification: 1.98 + 1.65 + 0.39 + 0.29 + 97.41 + 85.49 = 187.21 s, 1657856 kB

- Example 6: Double component, 4 proof inside the manifest encoded in Base64
        1. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        2. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        3. Proof name: 'mutestp.cpc' with original size of 24.5 MB, compressed 3.2 MB.
        4. Proof name: 'mutestiso.cpc" with original size of 27.7 MB, compressed 3.4 MB.
        SBOM: 34.7 kB
        Total size: 14.7 MB
        Parsing & signature: 2.55 s, 63488 kB
        Proofs verification: 97.41 + 85.49 + 162.51 + 142.36 = 487.77 s, 2713088 kB 

- Example 7: Triple component, 5 proof inside the manifest encoded in Base64
        1. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'hello01p.cpc', with original size of 476.2kB, compressed 72.0 kB.
        3. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        4. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        5. Proof name: 'mempart.cpc' with original size of 15.3 kB, compressed 2.7 kB. 
        SBOM: 34.7 kB
        Total size: 6.2 MB
        Parsing & signature: 1.15 s, 30720 kB
        Proofs verification: 1.98 + 1.65 + 97.41 + 85.49 + 0.29 = 186.82 s, 1657856 kB 

- Example 8: Triple component, 6 proof inside the manifest encoded in Base64
        1. Proof name: 'mempart.cpc' with original size of 15.3 kB, compressed 2.7 kB.
        2. Proof name: 'pic32mz2.cpc' with original size of 40.8kB, compressed 6.6kB.
        3. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        4. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        5. Proof name: 'mutestp.cpc' with original size of 24.5 MB, compressed 3.2 MB.
        6. Proof name: 'mutestiso.cpc" with original size of 27.7 MB, compressed 3.4 MB.
        SBOM: 34.7 kB
        Total size: 14.7 MB
        Parsing & signature: 2.54 s, 63488 kB
        Proofs verification: 0.39 + 0.29 + 97.41 + 85.49 + 162.51 + 142.36 = 488.45 s, 2713088 kB 

- Example 9: Triple component, 7 proof inside the manifest encoded in Base64
        1. Proof name: 'mempart.cpc' with original size of 15.3 kB, compressed 2.7 kB.
        2. Proof name: 'pic32mz2.cpc' with original size of 40.8kB, compressed 6.6kB.
        3. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        4. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        5. Proof name: 'mutestp.cpc' with original size of 24.5 MB, compressed 3.2 MB.
        6. Proof name: 'mutestiso.cpc" with original size of 27.7 MB, compressed 3.4 MB.
        7. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        SBOM: 34.7 kB
        Total size: 14.8 MB
        Parsing & signature: 2.58 s, 64512 kB
        Proofs verification: 0.39 + 0.29 + 97.41 + 85.49 + 162.51 + 142.36 + 1.98 = 490.43 s, 2713088 kB 

- Example 10: 10 component, 4 proof inside the manifest encoded in Base64
        1. Proof name: 'hello01iso.cpc', with original size of 562.8kB, compressed 83.3kB.
        2. Proof name: 'hello01p.cpc', with original size of 476.2kB, compressed 72.0 kB.
        3. Proof name: 'crciso.cpc', with original size of 18.4 MB, compressed 2.3 MB.
        4. Proof name: 'crcp.cpc', with original size of 16.2 MB, compressed 2.1 MB.
        SBOM: 2.4 kB
        Total size: 6.1 MB
        Parsing & signature: 1.07 s, 29184 kB
        Proofs verification: 1.98 + 1.65 + 97.41 + 85.49 = 186.53 s, 1657856 kB 


# Platform configuration

The parser and tests were executed on a Raspberry Pi4 running OP-TEE (porting guide: https://github.com/Jachm11/optee-os_raspberry_pi_4_port?tab=readme-ov-file). 

To use the device here are the steps:
- Connect the PC and the Raspberry Pi 4 (RPi4) using an Ethernet cable and enable IP sharing;
- Discover the IP address of the RPi4 using ARP (arp -a);
- SSH with user root and the IP discovered into the Raspberry;
- Use "rpi4test' as password;
- The SUIT parser, Ethos and all the needed source are stored in the (/etc folder). 

To copy data from/to the RPi4 use scp command with option -O. 