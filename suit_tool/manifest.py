# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright 2019-2022 ARM Limited or its affiliates
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
import collections
import binascii
import cbor2 as cbor
import json
import copy
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from collections import OrderedDict

import logging
LOG = logging.getLogger(__name__)

TreeBranch = []

ManifestKey = collections.namedtuple(
    'ManifestKey',
    [
        'json_key',
        'suit_key',
        'obj'
    ]
)
def to_bytes(s):
    if isinstance(s,bytes):
        return s
    try:
        return binascii.a2b_hex(s)
    except:
        try:
            return binascii.a2b_base64(s)
        except:
            if isinstance(s,str):
                return s.encode('utf-8')
            else:
                return str(s).encode('utf-8')

class SUITException(Exception):
    def __init__(self, m, data, tree_branch):
        super().__init__(m)
        self.data = data
        self.tree_branch = tree_branch

class SUITCommonInformation:
    def __init__(self):
        self.component_ids = []
        self.dependencies = []
        self.current_index = None
        self.indent_size = 4
    def component_id_to_index(self, cid):
        for i, c in enumerate(self.component_ids):
            if cid == c and i >= 0:
                return componentIndex(i)
        else:
            for i, d in enumerate(self.dependencies):
                if cid == d.digest and i >= 0:
                    return dependencyIndex(i)
            else:
                raise SUITException('Failed to calculate component/dependency index', cid, TreeBranch)        

suitCommonInfo = SUITCommonInformation()
one_indent = '    '

class SUITInt:
    def from_json(self, v):
        self.v = int(v)
        return self
    def to_json(self):
        return self.v
    def from_suit(self, v):
        TreeBranch.append(type(self))
        self.v = int(v)
        TreeBranch.pop()
        return self
    def to_suit(self):
        return self.v
    def to_debug(self, indent):
        return str(self.v)

class SUITPosInt(SUITInt):
    def from_json(self, v):
        TreeBranch.append(type(self))
        _v = int(v)
        # print (_v)
        if _v < 0:
            raise SUITException(
                m = 'Positive Integers must be >= 0. Got {}.'.format(_v),
                data = _v,
                tree_branch = TreeBranch
            )

        self.v = _v
        TreeBranch.pop()
        return self
    def from_suit(self, v):
        return self.from_json(v)

class SUITManifestDict:
    def mkfields(d):
        # rd = OderedDict()
        return {k: ManifestKey(*v) for k,v in d.items()}

    def __init__(self):
        pass

    def __eq__(self, rhs):
        if not isinstance(rhs, SUITManifestDict):
            return False
        for f, info in self.fields.items():
            if not (getattr(self,f,None) == getattr(rhs,f,None)):
                return False

        return True

    def from_json(self, data):
        for k, f in self.fields.items():
            v = data.get(f.json_key, None)
            setattr(self, k, f.obj().from_json(v) if v is not None else None)
        return self

    def to_json(self):
        j = OrderedDict()
        for k, f in self.fields.items():
            v = getattr(self, k)
            if v:
                j[f.json_key] = v.to_json()
        return j

    def from_suit(self, data):
        TreeBranch.append(type(self))
        for k, f in self.fields.items():
            TreeBranch.append(k)
            v = data.get(f.suit_key, None)
            d = f.obj().from_suit(v) if v is not None else None
            setattr(self, k, d)
            TreeBranch.pop()
        TreeBranch.pop()
        return self

    def to_suit(self):
        sd = OrderedDict()
        for k, f in self.fields.items():
            v = getattr(self, k)
            if v:
                sd[f.suit_key] = v.to_suit()
        return sd
    def to_debug(self, indent):
        s = '{'
        newindent = indent + one_indent

        for k, f in self.fields.items():
            v = getattr(self, k)
            if v:
                s += '\n{ind}/ {jk} / {sk}:'.format(ind=newindent, jk=f.json_key, sk=f.suit_key)
                s += v.to_debug(newindent) + ','
        s += '\n' + indent + '}'
        return s


class SUITManifestNamedList(SUITManifestDict):
    def from_suit(self, data):
        TreeBranch.append(type(self))
        for k, f in self.fields.items():
            TreeBranch.append(k)
            setattr(self, k, f.obj().from_suit(data[f.suit_key]))
            TreeBranch.pop()
        TreeBranch.pop()
        return self

    def to_suit(self):
        sd = [None] * (max([f.suit_key for k, f in self.fields.items()]) + 1)
        for k, f in self.fields.items():
            v = getattr(self, k)
            if v:
                sd[f.suit_key] = v.to_suit()
        return sd
    def to_debug(self, indent):
        newindent = indent + one_indent
        items = []
        for k, f in self.fields.items():
            v = getattr(self, k)
            if v:
                items.append('/ ' + f.json_key + ' / ' + v.to_debug(newindent))
        s = '[\n{newindent}{items}\n{indent}]'.format(
            newindent=newindent,
            indent=indent,
            items=',\n{newindent}'.format(newindent=newindent).join(items)
        )
        return s

class SUITKeyMap:
    def __eq__(self, rhs):
        return self.v == rhs.v
    def mkKeyMaps(m):
        return {v:k for k,v in m.items()}, m
    def to_json(self):
        return self.rkeymap[self.v]
    def from_json(self, d):
        self.v = self.keymap[d]
        return self
    def to_suit(self):
        return self.v
    def from_suit(self, d):
        TreeBranch.append(type(self))
        self.v = self.keymap[self.rkeymap[d]]
        TreeBranch.pop()
        return self
    def to_debug(self, indent):
        s = str(self.v) + ' / ' + json.dumps(self.to_json(),sort_keys = True) + ' /'
        return s

def SUITBWrapField(c):
    class SUITBWrapper:
        def to_suit(self):
            return cbor.dumps(self.v.to_suit(), canonical=True)
        def from_suit(self, d):
            TreeBranch.append(type(self))
            try:
                self.v = c().from_suit(cbor.loads(d))
            except SUITException as e:
                raise e
            except Exception as e:
                LOG.debug('At {}: failed to load "{}" as CBOR'.format(type(self),binascii.b2a_hex(d).decode('utf-8')))
                LOG.debug('Path: {}'.format(TreeBranch))
                # LOG.debug('At {}: failed to load "{}" as CBOR'.format(type(self),binascii.b2a_hex(d).decode('utf-8')))
                raise SUITException(
                    m = 'At {}: failed to load "{}" as CBOR'.format(type(self),binascii.b2a_hex(d).decode('utf-8')),
                    data = d,
                    tree_branch = TreeBranch
                )
            TreeBranch.pop()
            return self
        def to_json(self):
            return self.v.to_json()
        def from_json(self, d):
            self.v = c().from_json(d)
            return self
        def to_debug(self, indent):
            # s = 'h\''
            # s += binascii.b2a_hex(self.to_suit()).decode('utf-8')
            # s += '\' / '
            s = '<< '
            s += self.v.to_debug(indent)
            s += ' >>'
            return s

    return SUITBWrapper

class SUITManifestArray:
    def __init__(self):
        self.items=[]
    def __eq__(self, rhs):
        if not isinstance(rhs, SUITManifestArray):
            return False
        if len(self.items) != len(rhs.items):
            return False
        for a,b in zip(self.items, rhs.items):
            if not a == b:
                return False
        return True

    def from_json(self, data):
        self.items = []
        for d in data:
            self.items.append(self.field.obj().from_json(d))
        return self

    def to_json(self):
        j = []
        for i in self.items:
            j.append(i.to_json())
        return j

    def from_suit(self, data):
        self.items = []
        TreeBranch.append(type(self))
        for d in data:
            TreeBranch.append(len(self.items))
            self.items.append(self.field.obj().from_suit(d))
            TreeBranch.pop()
        TreeBranch.pop()
        return self

    def to_suit(self):
        l = []
        for i in self.items:
            l.append(i.to_suit())
        return l

    def append(self, element):
        if not isinstance(element, self.field.obj):
            raise Exception('element {} is not a {}'.format(element, self.field.obj))
        self.items.append(element)

    def to_debug(self, indent):
        newindent = indent + one_indent
        s = '[\n'
        s += ' ,\n'.join([newindent + v.to_debug(newindent) for v in self.items])
        s += '\n' + indent + ']'
        return s
class SUITBytes:
    def to_json(self):
        return binascii.b2a_hex(self.v).decode('utf-8')
    def from_json(self, d):
        self.v = to_bytes(d)
        return self
    def from_suit(self, d):
        self.v = bytes(d)
        return self
    def to_suit(self):
        return self.v
    def to_debug(self, indent):
        return 'h\'' + self.to_json() + '\''
    def __eq__(self, rhs):
        return self.v == rhs.v

class SUITUUID(SUITBytes):
    def from_json(self, d):
        self.v = uuid.UUID(d).bytes
        return self
    def from_suit(self, d):
        self.v = uuid.UUID(bytes=d).bytes
        return self
    def to_debug(self, indent):
        return 'h\'' + self.to_json() + '\' / ' + str(uuid.UUID(bytes=self.v)) + ' /'


class SUITRaw:
    def to_json(self):
        return self.v
    def from_json(self, d):
        self.v = d
        return self
    def to_suit(self):
        return self.v
    def from_suit(self, d):
        self.v = d
        return self
    def to_debug(self, indent):
        return str(self.v)

class SUITNil:
    def to_json(self):
        return None
    def from_json(self, d):
        if d is not None:
            raise Exception('Expected Nil')
        return self
    def to_suit(self):
        return None
    def from_suit(self, d):
        if d is not None:
            raise Exception('Expected Nil')
        return self
    def to_debug(self, indent):
        return 'F6 / nil /'

class SUITTStr(SUITRaw):
    def from_json(self, d):
        self.v = str(d)
        return self
    def from_suit(self, d):
        self.v = str(d)
        return self
    def to_debug(self, indent):
        return '\''+ str(self.v) + '\''

class SUITComponentId(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITBytes)
    def to_suit(self):
        return tuple(super(SUITComponentId, self).to_suit())

    def to_debug(self, indent):
        newindent = indent + one_indent
        s = '[' + ', '.join([v.to_debug(newindent) for v in self.items]) + ']'
        return s
    def __hash__(self):
        return hash(tuple([i.v for i in self.items]))

def mkBoolOrObj(cls):
    class BoolOrObj():
        def __eq__(self,rhs):
            return self.v.__eq__(rhs)
        def from_json(self, d):
            if isinstance(d, bool):
                self.v = d
            else:
                self.v = cls().from_json(d)
            return self
        def from_suit(self, d):
            if isinstance(d, bool):
                self.v = d
            else:
                self.v = cls().from_suit(d)
            return self
        def to_json(self):
            if isinstance(self.v, bool):
                return self.v
            else:
                return self.v.to_json()
        def to_suit(self):
            if isinstance(self.v, bool):
                return self.v
            else:
                return self.v.to_suit()

        def to_debug(self, indent):
            if isinstance(self.v, bool):
                return str(self.v)
            else:
                return self.v.to_debug(indent)
    return BoolOrObj

class SUITComponentIndex(SUITComponentId):
    def to_suit(self):
        return suitCommonInfo.component_id_to_index(self)
    def from_suit(self, d):
        return super(SUITComponentIndex, self).from_suit(
            suitCommonInfo.component_ids[d].to_suit()
        )
    def to_debug(self, indent):
        newindent = indent + one_indent
        s = '{suit} / [{dbg}] /'.format(
            suit=self.to_suit(),
            dbg=''.join([v.to_debug(newindent) for v in self.items])
        )
        return s

class SUITComponents(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITComponentId)

    def from_suit(self, data):
        super(SUITComponents, self).from_suit(data)
        suitCommonInfo.component_ids = self.items
        return self

    def from_json(self, j):
        super(SUITComponents, self).from_json(j)
        suitCommonInfo.component_ids = self.items
        return self

class SUITDigestAlgo(SUITKeyMap):
    rkeymap, keymap = SUITKeyMap.mkKeyMaps({
        'sha256' : -16,
        'sha384' : -43,
        'sha512' : -44,
        'shake128': -18,
        'shake256': -45,
    })

class SUITDigest(SUITManifestNamedList):
    fields = SUITManifestNamedList.mkfields({
        'algo' : ('algorithm-id', 0, SUITDigestAlgo),
        'digest' : ('digest-bytes', 1, SUITBytes)
    })
    def __hash__(self):
        return hash(tuple([getattr(self, k) for k in self.fields.keys() if hasattr(self, k)]))
    def __eq__(self, rhs):
        return super(SUITDigest, self).__eq__(rhs)

class SUITCompressionAlg(SUITKeyMap):
    rkeymap, keymap = SUITKeyMap.mkKeyMaps({
        'zlib' : 1,
        'bzip2' : 2,
        'deflate' : 3,
        'lz4' : 4,
        'lzma' : 7
    })

class SUITCompressionInfo(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'compression-algorithm' : ('compression-algorithm', 1, SUITCompressionAlg),
    })

class SUITParameters(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'vendor-id' : ('vendor-id', 1, SUITUUID),
        'class-id' : ('class-id', 2, SUITUUID),
        'digest' : ('image-digest', 3, SUITBWrapField(SUITDigest)),
        'size' : ('image-size', 14, SUITPosInt),
        'uri' : ('uri', 21, SUITTStr),
        'src' : ('source-component', 22, SUITComponentIndex),
        'compress' : ('compression-info', 19, SUITBWrapField(SUITCompressionInfo)),
        'slot' : ('slot', 5, SUITPosInt)
    })
    def from_json(self, j):
        return super(SUITParameters, self).from_json(j)

class SUITTryEach(SUITManifestArray):
    pass

class dependencyIndex(int):
    def __new__(cls, value):
        if isinstance(value, SUITPosInt):
            value = value.v
        return super(cls, cls).__new__(cls, value)
class componentIndex(int):
    def __new__(cls, value):
        if isinstance(value, SUITPosInt):
            value = value.v
        return super(cls, cls).__new__(cls, value)

def SUITCommandContainer(jkey, skey, argtype, dp=[]):
    class SUITCmd(SUITCommand):
        json_key = jkey
        suit_key = skey
        dep_params = dp
        def __init__(self):
            pass
        def to_suit(self):
            return [self.suit_key, self.arg.to_suit()]
        def to_json(self):
            if self.json_key == 'directive-set-component-index':
                return {}
            else:
                # check if self has a component id
                if hasattr(self, 'cid'):
                    return {
                        'command-id' : self.json_key,
                        'command-arg' : self.arg.to_json(),
                        'component-id' : self.cid.to_json()
                    }
                else:
                    return {
                        'command-id' : self.json_key,
                        'command-arg' : self.arg.to_json(),
                        'component-id' : None
                    }
        def from_json(self, j):
            if j['command-id'] != self.json_key:
                raise Except('JSON Key mismatch error')
            if self.json_key != 'directive-set-component-index' and self.json_key != 'directive-set-dependency-index':
                if isinstance(j['component-id'], list):
                    self.cid = mkBoolOrObj(SUITComponentId)().from_json(j['component-id'])
                else:
                    self.cid = mkBoolOrObj(SUITDigest)().from_json(j['component-id'])
            self.arg = argtype().from_json(j['command-arg'])
            return self
        def from_suit(self, s):
            if s[0] != self.suit_key:
                raise Except('SUIT Key mismatch error')
            if self.json_key == 'directive-set-component-index':
                suitCommonInfo.current_index = componentIndex(s[1])
            elif self.json_key == 'directive-set-dependency-index':
                suitCommonInfo.current_index = dependencyIndex(s[1])
            else:
                if isinstance(suitCommonInfo.current_index, dependencyIndex):
                    self.cid = suitCommonInfo.dependencies[suitCommonInfo.current_index].digest
                else:
                    self.cid = suitCommonInfo.component_ids[suitCommonInfo.current_index]
            self.arg = argtype().from_suit(s[1])
            return self
        def to_debug(self, indent):
            s = '/ {} / {},'.format(self.json_key, self.suit_key)
            s += self.arg.to_debug(indent)
            return s
    return SUITCmd

def mkPolicy(policy):
    class SUITReportingPolicy(SUITPosInt):
        default_policy = policy
        def from_json(self, j):
            if j is None:
                j = self.default_policy
            return super(SUITReportingPolicy, self).from_json(j)
    return SUITReportingPolicy

class SUITCommand:
    def from_json(self, j):
        return self.jcommands[j['command-id']]().from_json(j)
    def from_suit(self, s):
        return self.scommands[s[0]]().from_suit(s)

SUITCommand.commands = [
    SUITCommandContainer('condition-vendor-identifier',    1,  mkPolicy(policy=0xF), dp=['vendor-id']),
    SUITCommandContainer('condition-class-identifier',     2,  mkPolicy(policy=0xF), dp=['class-id']),
    SUITCommandContainer('condition-image-match',          3,  mkPolicy(policy=0xF), dp=['digest']),
    SUITCommandContainer('condition-use-before',           4,  mkPolicy(policy=0xA)),
    SUITCommandContainer('condition-component-slot',     5,  mkPolicy(policy=0x5), dp=['slot']),
    SUITCommandContainer('condition-device-identifier',    24, mkPolicy(policy=0xF)),
    SUITCommandContainer('condition-image-not-match',      25, mkPolicy(policy=0xF)),
    SUITCommandContainer('condition-minimum-battery',      26, mkPolicy(policy=0xA)),
    SUITCommandContainer('condition-update-authorised',    27, mkPolicy(policy=0x3)),
    SUITCommandContainer('condition-version',              28, mkPolicy(policy=0xF)),
    SUITCommandContainer('directive-set-component-index',  12, mkBoolOrObj(SUITPosInt)),
    SUITCommandContainer('directive-set-dependency-index', 13, mkBoolOrObj(SUITPosInt)),
    SUITCommandContainer('directive-abort',                14, mkPolicy(policy=0x2)),
    SUITCommandContainer('directive-try-each',             15, SUITTryEach),
    SUITCommandContainer('directive-process-dependency',   18, mkPolicy(policy=0)),
    SUITCommandContainer('directive-set-parameters',       19, SUITParameters),
    SUITCommandContainer('directive-override-parameters',  20, SUITParameters),
    SUITCommandContainer('directive-fetch',                21, mkPolicy(policy=0x2)),
    SUITCommandContainer('directive-copy',                 22, mkPolicy(policy=0x2)),
    SUITCommandContainer('directive-run',                  23, mkPolicy(policy=0x2)),
    SUITCommandContainer('directive-wait',                 29, mkPolicy(policy=0x2)),
    SUITCommandContainer('directive-run-sequence',         30, SUITRaw),
    SUITCommandContainer('directive-run-with-arguments',   31, SUITRaw),
    SUITCommandContainer('directive-swap',                 32, mkPolicy(policy=0x2)),
]
SUITCommand.jcommands = { c.json_key : c for c in SUITCommand.commands}
SUITCommand.scommands = { c.suit_key : c for c in SUITCommand.commands}

class SUITSequence(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITCommand)
    def to_suit(self):
        suit_l = []
        for i in self.items:
            if i.json_key == 'directive-set-component-index':
                suitCommonInfo.current_index = componentIndex(i.arg.v)
            elif i.json_key == 'directive-set-dependency-index':
                suitCommonInfo.current_index = dependencyIndex(i.arg.v)
            else:
                # Option 1: current & command index same class, same number,
                    # Do nothing 
                # Option 2: current & command not equal, command is component
                    # set component index
                # Option 3: current & command not equal, command is dependency
                    # set dependency index
                current_index = suitCommonInfo.current_index
                cidx = suitCommonInfo.component_id_to_index(i.cid)
                if not isinstance(cidx, type(current_index)) or not (cidx == current_index):
                    op = 'directive-set-component-index'
                    if isinstance(cidx, dependencyIndex):
                        op = 'directive-set-dependency-index'
                    # Change component/dependency
                    suitCommonInfo.current_index = cidx
                    suit_l += SUITCommand().from_json({
                        'command-id' : op,
                        'command-arg' : int(cidx)
                    }).to_suit()
            suit_l += i.to_suit()
        return suit_l
    def to_debug(self, indent):
        return super(SUITSequence, SUITSequence().from_suit(self.to_suit())).to_debug(indent)
    def from_suit(self, s):
        self.items = [SUITCommand().from_suit(i) for i in zip(*[iter(s)]*2)]
        return self

SUITTryEach.field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITBWrapField(SUITSequence))

class SUITSequenceComponentReset(SUITSequence):
    def reset_idx(self):
        if len(suitCommonInfo.component_ids) == 1 and len(suitCommonInfo.dependencies) == 0:
            suitCommonInfo.current_index = componentIndex(0)
        elif len(suitCommonInfo.component_ids) == 0 and len(suitCommonInfo.dependencies) == 1:
            suitCommonInfo.current_index = dependencyIndex(0)
        else:
            suitCommonInfo.current_index = None
    def to_suit(self):
        self.reset_idx()
        return super(SUITSequenceComponentReset, self).to_suit()
    def from_suit(self, data):
        self.reset_idx()
        return super(SUITSequenceComponentReset, self).from_suit(data)

def SUITMakeSeverableField(c):
    class SUITSeverableField:
        objtype = SUITBWrapField(c)
        def from_json(self, data):
            if 'algorithm-id' in data:
                self.v = SUITDigest().from_json(data)
            else:
                self.v = self.objtype().from_json(data)
            return self
        def from_suit(self, data):
            if isinstance(data, list):
                self.v = SUITDigest().from_suit(data)
            else:
                self.v = self.objtype().from_suit(data)
            return self
        def to_json(self):
            return self.v.to_json()
        def to_suit(self):
            return self.v.to_suit()
        def to_debug(self, indent):
            return self.v.to_debug(indent)
    return SUITSeverableField

class SUITDependency(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'digest' : ('dependency-digest', 1, SUITDigest),
        'prefix' : ('dependency-prefix', 2, SUITComponentId),
    })

class SUITDependencies(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITDependency)

    def from_suit(self, data):
        super(SUITDependencies, self).from_suit(data)
        suitCommonInfo.dependencies = self.items
        return self

    def from_json(self, j):
        super(SUITDependencies, self).from_json(j)
        suitCommonInfo.dependencies = self.items
        return self

class SUITCommon(SUITManifestDict):
    fields = SUITManifestNamedList.mkfields({
        'dependencies' : ('dependencies', 1, SUITDependencies),
        'components' : ('components', 2, SUITComponents),
        'common_sequence' : ('common-sequence', 4, SUITBWrapField(SUITSequenceComponentReset)),
    })

class SUITComponentText(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'vendorname' : ('vendor-name', 1, SUITTStr),
        'modelname' : ('model-name', 2, SUITTStr),
        'vendordomain' : ('vendor-domain', 3, SUITTStr),
        'modelinfo' : ('json-source', 4, SUITTStr),
        'cdesc' : ('component-description', 5, SUITTStr),
        'version' : ('version', 6, SUITTStr),
        'reqversion' : ('required-version', 7, SUITTStr),
    })

class SUITVerificationServerURI(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'uri': ('uri', 1, SUITTStr),
    })

class SUITVerificationServers(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITVerificationServerURI)

class SUITProofDescriptor(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'propid': ('property-id', 1, SUITUUID),
        'langid': ('language-id', 2, SUITTStr),
        'compid': ('component-id', 3, SUITComponentId),
        'proof_cert': ('proof-certificate', 4, SUITRaw), # Evaluate SUITRaw or SUITBytes
        'local_constr': ('locality-constraint', 5, SUITInt),
        'verif_servers': ('verification-servers', 6, SUITVerificationServers),
    })

class SUITCertificationManifest(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITProofDescriptor)

class SUITText(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'mdesc' : ('manifest-description', 1, SUITTStr),
        'udesc' : ('update-description', 2, SUITTStr),
        'json' : ('json-source', 3, SUITTStr),
        'yaml' : ('yaml-source', 4, SUITTStr),
        'sbom' : ('software-bill-of-materials', -256, SUITTStr),
    })
    components={}

    def to_json(self):
        d = super(SUITText, self).to_json()
        d.update({tuple(k.to_json()) : tuple(v.to_json()) for k,v in self.components.items()})
        return d

    def from_json(self, data):
        # Handle components
        for k,v in data.items():
            if not isinstance(v, str):
                self.components[SUITComponentId().from_json(k)] = SUITComponentText().from_json(v)
        # Treat everything else as a normal manifestDict
        return super(SUITText, self).from_json(data)

    def to_suit(self):
        d = super(SUITText, self).to_suit()
        d.update({k.to_suit() : v.to_suit() for k,v in self.components.items()})
        return d

    def from_suit(self, data):
        # Handle components
        for k,v in data.items():
            if not isinstance(v, str):
                self.components[SUITComponentId().from_suit(k)] = SUITComponentText().from_suit(v)
        # Treat everything else as a normal manifestDict
        return super(SUITText, self).from_json(data)
    
    def to_debug(self, indent):
        s = '{'
        newindent = indent + one_indent

        for k, f in self.fields.items():
            v = getattr(self, k)
            if v:
                s += '\n{ind}/ {jk} / {sk}:'.format(ind=newindent, jk=f.json_key, sk=f.suit_key)
                s += v.to_debug(newindent) + ','
        for k, f in self.components.items():
            s += '\n' + newindent + '{}:'.format(k.to_debug(newindent + one_indent))
            s += f.to_debug(newindent + one_indent)

        s += '\n' + indent + '}'

        return s


class SUITManifest(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'version' : ('manifest-version', 1, SUITPosInt),
        'sequence' : ('manifest-sequence-number', 2, SUITPosInt),
        'common' : ('common', 3, SUITBWrapField(SUITCommon)),
        'refuri' : ('reference-uri', 4, SUITTStr), 

        'validate' : ('validate', 7, SUITBWrapField(SUITSequenceComponentReset)),
        'load' : ('load', 8, SUITBWrapField(SUITSequenceComponentReset)),
        'run' : ('run', 9, SUITBWrapField(SUITSequenceComponentReset)),

        'deres' : ('dependency-resolution', 15, SUITMakeSeverableField(SUITSequenceComponentReset)),
        'fetch' : ('payload-fetch', 16, SUITMakeSeverableField(SUITSequenceComponentReset)),
        'install' : ('install', 17, SUITMakeSeverableField(SUITSequenceComponentReset)),

        'text' : ('text', 23, SUITMakeSeverableField(SUITText)),
        'coswid' : ('coswid', 24, SUITBytes),

        'certman' : ('certification-manifest', 25, SUITBWrapField(SUITCertificationManifest)),
    })

class COSE_Algorithms(SUITKeyMap):
    rkeymap, keymap = SUITKeyMap.mkKeyMaps({
        'ES256' : -7,
        'ES384' : -35,
        'ES512' : -36,
        'EdDSA' : -8,
        'HSS-LMS' : -46,
    })

class COSE_CritList(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITInt)

class COSE_header_map(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        # 1: algorithm Identifier
        'alg' : ('alg', 1, COSE_Algorithms),
        # 2: list of critical headers (criticality)
        # 3: content type
        # 4: key id
        'kid' : ('kid', 4, SUITBytes),
        # 5: IV
        # 6: partial IV
        # 7: counter signature(s)
    })

class COSE_Sign:
    pass
class COSE_Sign1(SUITManifestNamedList):
    fields = SUITManifestDict.mkfields({
        'protected' : ('protected', 0, SUITBWrapField(COSE_header_map)),
        'unprotected' : ('unprotected', 1, COSE_header_map),
        'payload' : ('payload', 2, SUITNil),
        'signature' : ('signature', 3, SUITBytes)
    })
class COSE_Mac:
    pass
class COSE_Mac0:
    pass

class COSETagChoice(SUITManifestDict):
    def to_suit(self):
        for k, f in self.fields.items():
            v = getattr(self, k, None)
            if v:
                return cbor.CBORTag(tag=f.suit_key, value=v.to_suit())
        return None

    def from_suit(self, data):
        for k, f in self.fields.items():
            if data.tag == f.suit_key:
                v = data.value
                d = f.obj().from_suit(v) if v is not None else None
                setattr(self, k, d)
        return self

    def to_debug(self, indent):
        s = ''
        for k, f in self.fields.items():
            if hasattr(self, k):
                v = getattr(self, k)
                newindent = indent + one_indent
                s = '{tag}({value})'.format(tag=f.suit_key, value=v.to_debug(newindent))
        return s

class COSETaggedAuth(COSETagChoice):
    fields = SUITManifestDict.mkfields({
        #'cose_sign' : ('COSE_Sign_Tagged', 98, COSE_Sign),
        'cose_sign1' : ('COSE_Sign1_Tagged', 18, COSE_Sign1),
        #'cose_mac' : ('COSE_Mac_Tagged', 97, COSE_Mac),
        #'cose_mac0' : ('COSE_Mac0_Tagged', 17, COSE_Mac0)
    })

class COSEList(SUITManifestArray):
    field = collections.namedtuple('ArrayElement', 'obj')(obj=SUITBWrapField(COSETaggedAuth))
    digestType = SUITBWrapField(SUITDigest)
    def from_suit(self, data):
        if len(data):
            self.digest = self.digestType().from_suit(data[0])
        return super(COSEList, self).from_suit(data[1:])

    def to_suit(self):
        return [x.digest.to_suit() for x in [self] if hasattr(x, 'digest')] + super(COSEList, self).to_suit()
    def from_json(self, data):
        if len(data):
            self.digest = self.digestType().from_json(data[0])
        return super(COSEList, self).from_json(data[1:])
    def to_json(self):
        return [self.digest.to_json()] + super(COSEList, self).to_json()
    def to_debug(self, indent):
        s = '[\n'
        indent1 = indent + one_indent
        # show digest
        if hasattr(self,'digest'):
            s += indent1 + '/ digest: / ' + self.digest.to_debug(indent1)
            if len(self.items):
                s += ',\n'
        # show signatures
        # s += indent1 + 'signatures: [\n'
        indent2 = indent1
        s += ' ,\n'.join([indent2 + '/ signature: / ' + v.to_debug(indent2) for v in self.items])
        s += '\n' + indent1 + ']'
        s += '\n{}]'.format(indent)
        return s 

class SUITEnvelope(SUITManifestDict):
    fields = SUITManifestDict.mkfields({
        'auth' : ('authentication-wrapper', 2, SUITBWrapField(COSEList)),
        'manifest' : ('manifest', 3, SUITBWrapField(SUITManifest)),

        'validate': ('validate', 7, SUITBWrapField(SUITSequence)),
        'load': ('load', 8, SUITBWrapField(SUITSequence)),
        'run': ('run', 9, SUITBWrapField(SUITSequence)),

        'deres': ('dependency-resolution', 15, SUITBWrapField(SUITSequence)),
        'fetch': ('payload-fetch', 16, SUITBWrapField(SUITSequence)),
        'install': ('install', 17, SUITBWrapField(SUITSequence)),

        'text': ('text', 23, SUITBWrapField(SUITText)),
        'coswid': ('coswid', 14, SUITBytes),
    })
    severable_fields = {'deres', 'fetch', 'install', 'text', 'coswid'}
    digest_algorithms = {
        'sha224' : hashes.SHA224,
        'sha256' : hashes.SHA256,
        'sha384' : hashes.SHA384,
        'sha512' : hashes.SHA512
    }
    def to_severable(self, digest_alg):
        sev = copy.deepcopy(self)
        for k in sev.severable_fields:
            f = sev.manifest.v.fields[k]
            if not hasattr(sev.manifest.v, k):
                continue
            v = getattr(sev.manifest.v, k)
            if v is None:
                continue
            cbor_field = cbor.dumps(v.to_suit(), canonical=True)
            digest = hashes.Hash(self.digest_algorithms.get(digest_alg)(), backend=default_backend())
            digest.update(cbor_field)
            field_digest = SUITDigest().from_json({
                'algorithm-id' : digest_alg,
                'digest-bytes' : digest.finalize()
            })
            cbor_digest = cbor.dumps(field_digest.to_suit(), canonical=True)
            if len(cbor_digest) < len(cbor_field):
                setattr(sev.manifest.v, k, field_digest)
                setattr(sev,k,v)
        return sev
    def from_severable(self):
        raise Exception('From Severable unimplemented')
        nsev = copy.deepcopy(self)
        for k in nsev.severable_fields:
            f = nsev.fields[k]
            if not hasattr(nsev, k):
                continue
            v = getattr(nsev, k)
            if v is None:
                continue
            # Verify digest
            cbor_field = cbor.dumps(v.to_suit(), canonical=True)
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(cbor_field)
            actual_digest = digest.finalize()
            field_digest = getattr(nsev.v, k)
            expected_digest = field_digest.to_suit()[1]
            if digest != expected_digest:
                raise Exception('Field Digest mismatch: For {}, expected: {}, got {}'.format(
                    f.json_key, expected_digest, actual_digest
                ))
            setattr(nsev.manifest.v, k, v)
            delattr(nsev, k)
        return nsev

class SUITEnvelopeTagged(COSETagChoice):
    fields = SUITManifestDict.mkfields({
        'suit_envelope' : ('SUITEnvelope_Tagged', 107, SUITEnvelope),
    })