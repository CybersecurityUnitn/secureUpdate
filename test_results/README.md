# Test results 
    
This folder contains the timing results of parsing and proof verification
steps for the SUIT manifests provided in the `example` folder.
The tests were executed on a Raspberry Pi 4B running OP-TEE (porting guide:
https://github.com/Jachm11/optee-os_raspberry_pi_4_port?tab=readme-ov-file).


## Platform configuration

To use the device here are the steps:
- Connect the PC and the Raspberry Pi 4 (RPi4) using an Ethernet cable and enable IP sharing;
- Discover the IP address of the RPi4 using ARP (arp -a);
- SSH with user root and the IP discovered into the Raspberry;
- Use `rpi4test` as password;
- The script to verify the proofs is stored in the `/etc/proofs` folder;
- The script to validate the manifests is stored in the `/etc/SecureUpdate` folder.

To copy data from/to the RPi4 use scp command with option -O. 
