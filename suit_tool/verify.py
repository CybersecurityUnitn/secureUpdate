#!/usr/bin/env python3

import cbor2 as cbor
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import utils as asymmetric_utils
from cryptography.hazmat.primitives import serialization as ks

import pyhsslms

from suit_tool.manifest import COSE_Sign1, COSEList, SUITDigest,\
                               SUITEnvelope, SUITEnvelopeTagged, SUITBytes, SUITBWrapField, \
                               COSETaggedAuth
import logging
import binascii
LOG = logging.getLogger(__name__)

def extract_signature_bytes(data):
    data = data.to_json()
    signature_bytes = data['SUITEnvelope_Tagged']['authentication-wrapper'][1]['COSE_Sign1_Tagged']['signature']
    if not signature_bytes:
        raise ValueError("Signature not found in the file")
    return signature_bytes

def verify_cose_es_signature(options, public_key, sig_val, signature_bytes):
    LOG.debug('Verifying ECDSA signature')
    try:
        # Extract 'r' and 's' from the signature bytes
        ssize = public_key.key_size
        signature_bytes = binascii.a2b_hex(signature_bytes)
        r = int.from_bytes(signature_bytes[:ssize // 8], byteorder='big')
        s = int.from_bytes(signature_bytes[ssize // 8:], byteorder='big')
        # Encode 'r' and 's' into DER format
        der_signature = asymmetric_utils.encode_dss_signature(r, s)
        # Verify the signature using the public key
        public_key.verify(der_signature, sig_val, ec.ECDSA(hashes.SHA256()), )
        return True
    except Exception as e:
        LOG.error('Signature verification failed {}'.format(e))
        return False
    
def verify_cose_ed25519_bytes(options, public_key, sig_val, signature_bytes):
    LOG.debug('Verifying EdDSA signature')
    try:
        public_key.verify(binascii.a2b_hex(signature_bytes), sig_val)
        return True
    except Exception as e:
        LOG.error('Signature verification failed {}'.format(e))
        return False

def main(options):
    
    # Read the manifest wrapper
    wrapper =  cbor.loads(options.signature.read())
    # Create a deep copy of the wrapper
    signed_wrapper = cbor.loads(cbor.dumps(wrapper))
    
    signature_bytes = extract_signature_bytes(SUITEnvelopeTagged().from_suit(signed_wrapper))

    public_key = None
    digest = None

    public_key_buffer = options.public_key.read()
    #print(public_key_buffer)

    try:
        public_key = ks.load_pem_public_key(public_key_buffer, backend=default_backend())
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            options.key_type = 'ES{}'.format(public_key.key_size)
        elif isinstance(public_key, ed25519.Ed25519PublicKey):
            options.key_type = 'EdDSA'
        else:
            LOG.critical('Unrecognized key: {}'.format(type(public_key).__name__))
            return 1
        digest = {
            'ES256' : hashes.Hash(hashes.SHA256(), backend=default_backend()),
            'ES384' : hashes.Hash(hashes.SHA384(), backend=default_backend()),
            'ES512' : hashes.Hash(hashes.SHA512(), backend=default_backend()),
            'EdDSA' : hashes.Hash(hashes.SHA256(), backend=default_backend()),
        }.get(options.key_type)
    except:
        # NOT SUPPORTED
        #try:
        #    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        #    public_key = pyhsslms.HssLmsPublicKey.deserialize(public_key_buffer)
        #    options.key_type = 'HSS-LMS'
        #except:
        LOG.critical('Non-library key type not implemented')
        return 1

    #print(cbor.dumps(wrapper[SUITEnvelope.fields['manifest'].suit_key]))
    auth = SUITBWrapField(COSEList)().from_suit(wrapper.value[SUITEnvelope.fields['auth'].suit_key])
    payload_digest = auth.v.digest
    digest.update(cbor.dumps(wrapper.value[SUITEnvelope.fields['manifest'].suit_key]))

    cose_signature = COSE_Sign1().from_json({
        'protected' : {
            'alg' : options.key_type
        },
        'unprotected' : {},
        'payload' : None
        # 'payload' : {
        #     'algorithm-id' : 'sha256',
        #     'digest-bytes' : binascii.b2a_hex(digest.finalize()).decode('utf-8')
        # }
    })

    Sig_structure = cbor.dumps([
        "Signature1",
        cose_signature.protected.to_suit(),
        b'',
        payload_digest.to_suit(),
    ], canonical = True)
    LOG.debug('Verifying: {}'.format(binascii.b2a_hex(Sig_structure).decode('utf-8'))) 

    res = {
        'ES256' : verify_cose_es_signature,
        'ES384' : verify_cose_es_signature,
        'ES512' : verify_cose_es_signature,
        'EdDSA' : verify_cose_ed25519_bytes,
        #'HSS-LMS' : get_hsslms_bytes, // NOT SUPPORTED
    }.get(options.key_type)(options, public_key, Sig_structure, signature_bytes)
    
    if res:
        options.output_file.write("Signature verified successfully\n")
    else:
        options.output_file.write("Signature verification failed\n")
    
    return 0