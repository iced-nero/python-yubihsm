# Copyright 2016-2018 Yubico AB
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

from yubihsm.defs import ALGORITHM, CAPABILITY
from yubihsm.objects import HmacKey
import random
import os
import pytest


@pytest.mark.parametrize(
    "algorithm, expect_len",
    [
        (ALGORITHM.HMAC_SHA1, 20),
        (ALGORITHM.HMAC_SHA256, 32),
        (ALGORITHM.HMAC_SHA384, 48),
        (ALGORITHM.HMAC_SHA512, 64),
    ],
)
def test_generate_hmac(session, algorithm, expect_len):
    caps = CAPABILITY.SIGN_HMAC | CAPABILITY.VERIFY_HMAC
    hmackey = HmacKey.generate(session, 0, "Generate HMAC", 1, caps, algorithm)

    data = os.urandom(64)

    resp = hmackey.sign_hmac(data)
    assert len(resp) == expect_len
    assert hmackey.verify_hmac(resp, data)

    resp2 = hmackey.sign_hmac(data)
    assert len(resp2) == expect_len
    assert resp == resp2

    data = os.urandom(64)
    resp2 = hmackey.sign_hmac(data)
    assert len(resp2) == expect_len
    assert resp != resp2
    assert hmackey.verify_hmac(resp2, data)

    hmackey.delete()

    hmackey = HmacKey.generate(session, 0, "Generate HMAC", 1, caps, algorithm)

    resp = hmackey.sign_hmac(data)
    assert len(resp) == expect_len
    assert resp != resp2
    assert hmackey.verify_hmac(resp, data)

    hmackey.delete()


@pytest.mark.parametrize(
    "vector",
    [
        {
            "key": b"\x0b" * 20,
            "chal": b"Hi There",
            "exp_sha1": b"\xb6\x17\x31\x86\x55\x05\x72\x64\xe2\x8b\xc0\xb6\xfb\x37\x8c\x8e\xf1\x46\xbe\x00",  # noqa: E501
            "exp_sha256": b"\xb0\x34\x4c\x61\xd8\xdb\x38\x53\x5c\xa8\xaf\xce\xaf\x0b\xf1\x2b\x88\x1d\xc2\x00\xc9\x83\x3d\xa7\x26\xe9\x37\x6c\x2e\x32\xcf\xf7",  # noqa: E501
            "exp_sha512": b"\x87\xaa\x7c\xde\xa5\xef\x61\x9d\x4f\xf0\xb4\x24\x1a\x1d\x6c\xb0\x23\x79\xf4\xe2\xce\x4e\xc2\x78\x7a\xd0\xb3\x05\x45\xe1\x7c\xde\xda\xa8\x33\xb7\xd6\xb8\xa7\x02\x03\x8b\x27\x4e\xae\xa3\xf4\xe4\xbe\x9d\x91\x4e\xeb\x61\xf1\x70\x2e\x69\x6c\x20\x3a\x12\x68\x54",  # noqa: E501
            "exp_sha384": b"\xaf\xd0\x39\x44\xd8\x48\x95\x62\x6b\x08\x25\xf4\xab\x46\x90\x7f\x15\xf9\xda\xdb\xe4\x10\x1e\xc6\x82\xaa\x03\x4c\x7c\xeb\xc5\x9c\xfa\xea\x9e\xa9\x07\x6e\xde\x7f\x4a\xf1\x52\xe8\xb2\xfa\x9c\xb6",  # noqa: E501
        },
        {
            "key": b"Jefe",
            "chal": b"what do ya want for nothing?",
            "exp_sha1": b"\xef\xfc\xdf\x6a\xe5\xeb\x2f\xa2\xd2\x74\x16\xd5\xf1\x84\xdf\x9c\x25\x9a\x7c\x79",  # noqa: E501
            "exp_sha256": b"\x5b\xdc\xc1\x46\xbf\x60\x75\x4e\x6a\x04\x24\x26\x08\x95\x75\xc7\x5a\x00\x3f\x08\x9d\x27\x39\x83\x9d\xec\x58\xb9\x64\xec\x38\x43",  # noqa: E501
            "exp_sha512": b"\x16\x4b\x7a\x7b\xfc\xf8\x19\xe2\xe3\x95\xfb\xe7\x3b\x56\xe0\xa3\x87\xbd\x64\x22\x2e\x83\x1f\xd6\x10\x27\x0c\xd7\xea\x25\x05\x54\x97\x58\xbf\x75\xc0\x5a\x99\x4a\x6d\x03\x4f\x65\xf8\xf0\xe6\xfd\xca\xea\xb1\xa3\x4d\x4a\x6b\x4b\x63\x6e\x07\x0a\x38\xbc\xe7\x37",  # noqa: E501
            "exp_sha384": b"\xaf\x45\xd2\xe3\x76\x48\x40\x31\x61\x7f\x78\xd2\xb5\x8a\x6b\x1b\x9c\x7e\xf4\x64\xf5\xa0\x1b\x47\xe4\x2e\xc3\x73\x63\x22\x44\x5e\x8e\x22\x40\xca\x5e\x69\xe2\xc7\x8b\x32\x39\xec\xfa\xb2\x16\x49",  # noqa: E501
        },
        {
            "key": b"\xaa" * 20,
            "chal": b"\xdd" * 50,
            "exp_sha1": b"\x12\x5d\x73\x42\xb9\xac\x11\xcd\x91\xa3\x9a\xf4\x8a\xa1\x7b\x4f\x63\xf1\x75\xd3",  # noqa: E501
            "exp_sha256": b"\x77\x3e\xa9\x1e\x36\x80\x0e\x46\x85\x4d\xb8\xeb\xd0\x91\x81\xa7\x29\x59\x09\x8b\x3e\xf8\xc1\x22\xd9\x63\x55\x14\xce\xd5\x65\xfe",  # noqa: E501
            "exp_sha512": b"\xfa\x73\xb0\x08\x9d\x56\xa2\x84\xef\xb0\xf0\x75\x6c\x89\x0b\xe9\xb1\xb5\xdb\xdd\x8e\xe8\x1a\x36\x55\xf8\x3e\x33\xb2\x27\x9d\x39\xbf\x3e\x84\x82\x79\xa7\x22\xc8\x06\xb4\x85\xa4\x7e\x67\xc8\x07\xb9\x46\xa3\x37\xbe\xe8\x94\x26\x74\x27\x88\x59\xe1\x32\x92\xfb",  # noqa: E501
            "exp_sha384": b"\x88\x06\x26\x08\xd3\xe6\xad\x8a\x0a\xa2\xac\xe0\x14\xc8\xa8\x6f\x0a\xa6\x35\xd9\x47\xac\x9f\xeb\xe8\x3e\xf4\xe5\x59\x66\x14\x4b\x2a\x5a\xb3\x9d\xc1\x38\x14\xb9\x4e\x3a\xb6\xe1\x01\xa3\x4f\x27",  # noqa: E501
        },
        {
            "key": b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19",  # noqa: E501
            "chal": b"\xcd" * 50,
            "exp_sha1": b"\x4c\x90\x07\xf4\x02\x62\x50\xc6\xbc\x84\x14\xf9\xbf\x50\xc8\x6c\x2d\x72\x35\xda",  # noqa: E501
            "exp_sha256": b"\x82\x55\x8a\x38\x9a\x44\x3c\x0e\xa4\xcc\x81\x98\x99\xf2\x08\x3a\x85\xf0\xfa\xa3\xe5\x78\xf8\x07\x7a\x2e\x3f\xf4\x67\x29\x66\x5b",  # noqa: E501
            "exp_sha512": b"\xb0\xba\x46\x56\x37\x45\x8c\x69\x90\xe5\xa8\xc5\xf6\x1d\x4a\xf7\xe5\x76\xd9\x7f\xf9\x4b\x87\x2d\xe7\x6f\x80\x50\x36\x1e\xe3\xdb\xa9\x1c\xa5\xc1\x1a\xa2\x5e\xb4\xd6\x79\x27\x5c\xc5\x78\x80\x63\xa5\xf1\x97\x41\x12\x0c\x4f\x2d\xe2\xad\xeb\xeb\x10\xa2\x98\xdd",  # noqa: E501
            "exp_sha384": b"\x3e\x8a\x69\xb7\x78\x3c\x25\x85\x19\x33\xab\x62\x90\xaf\x6c\xa7\x7a\x99\x81\x48\x08\x50\x00\x9c\xc5\x57\x7c\x6e\x1f\x57\x3b\x4e\x68\x01\xdd\x23\xc4\xa7\xd6\x79\xcc\xf8\xa3\x86\xc6\x74\xcf\xfb",  # noqa: E501
        },
    ],
)
def test_hmac_vectors(session, vector):
    key1_id, key2_id, key3_id, key4_id = random.sample(range(1, 0xFFFE), 4)

    caps = CAPABILITY.SIGN_HMAC | CAPABILITY.VERIFY_HMAC

    key1 = HmacKey.put(
        session,
        key1_id,
        "Test HMAC Vectors 0x%04x" % key1_id,
        1,
        caps,
        vector["key"],
        ALGORITHM.HMAC_SHA1,
    )
    key2 = HmacKey.put(
        session,
        key2_id,
        "Test HMAC Vectors 0x%04x" % key2_id,
        1,
        caps,
        vector["key"],
        ALGORITHM.HMAC_SHA256,
    )
    key3 = HmacKey.put(
        session,
        key3_id,
        "Test HMAC Vectors 0x%04x" % key3_id,
        1,
        caps,
        vector["key"],
        ALGORITHM.HMAC_SHA384,
    )
    key4 = HmacKey.put(
        session,
        key4_id,
        "Test HMAC Vectors 0x%04x" % key4_id,
        1,
        caps,
        vector["key"],
        ALGORITHM.HMAC_SHA512,
    )

    assert key1.sign_hmac(vector["chal"]) == vector["exp_sha1"]
    assert key2.sign_hmac(vector["chal"]) == vector["exp_sha256"]
    assert key3.sign_hmac(vector["chal"]) == vector["exp_sha384"]
    assert key4.sign_hmac(vector["chal"]) == vector["exp_sha512"]
    assert key1.verify_hmac(vector["exp_sha1"], vector["chal"])
    assert key2.verify_hmac(vector["exp_sha256"], vector["chal"])
    assert key3.verify_hmac(vector["exp_sha384"], vector["chal"])
    assert key4.verify_hmac(vector["exp_sha512"], vector["chal"])

    key1.delete()
    key2.delete()
    key3.delete()
    key4.delete()


@pytest.mark.parametrize(
    "vector",
    [
        {
            "key": b"\x0b" * 65,  # Larger than SHA1 block size (64)
            "chal": b"\xdd" * 50,
            "algorithm": ALGORITHM.HMAC_SHA1,
            "exp_sha": b"<D\x87\x828\x8eW&\x03\xa1\xa8\x9a\x0bmy\x81\xfa\xffD\xed",  # noqa: E501
        },
        {
            "key": b"\xcd" * 65,  # Larger than SHA256 block size (64),
            "chal": b"\xab" * 50,
            "algorithm": ALGORITHM.HMAC_SHA256,
            "exp_sha": b"T\x15\xaf\xc0\xb8\xda\x95\x97pb_\xe6$\xea\xe1rR\xfe\\\r\x11(\xbe\x02\x06\x1a&l\xc9\x94\x95\x13",  # noqa: E501
        },
        {
            "key": b"\xde" * 129,  # Larger than SHA384 block size (128)
            "chal": b"\xbb" * 50,
            "algorithm": ALGORITHM.HMAC_SHA384,
            "exp_sha": b'`H\x9f\xfd\x99"\x86\x15\x1e\x80O\x0c\x19\xe9gH\xbck\xb57\x82\x16G42%6\xdcs\x82\xc8I\xcb|1\x1ftU\xfbb\x1c\x8b\xfb;"\xb6A\xb4',  # noqa: E501
        },
        {
            "key": b"\xcc" * 129,  # Larger than SHA512 block size (128)
            "chal": b"\xac" * 50,
            "algorithm": ALGORITHM.HMAC_SHA512,
            "exp_sha": b"1\xe2\x94\x08\xa0\xefF\x01Y\xeb\x9e\xc7\xe5\x807\xc9\xd7~Y\xd9\x83pM\xe5\x0eU\x94\xe4\xf1/\xa9J\xb97r\xf5\x16\x0f\xe62\x88\xcd\x14\xee\xd7\x1b|I\xe7\xbd\x8a\x12*H\x9b\xeb\x00\xa0-V\x05dn\x16",  # noqa: E501
        },
    ],
)
def test_import_large_keys(session, vector):
    key_id = random.randint(1, 0xFFFE)

    caps = CAPABILITY.SIGN_HMAC | CAPABILITY.VERIFY_HMAC

    key = HmacKey.put(
        session,
        key_id,
        "Test import large key 0x%04x" % key_id,
        1,
        caps,
        vector["key"],
        vector["algorithm"],
    )

    assert key.sign_hmac(vector["chal"]) == vector["exp_sha"]
    assert key.verify_hmac(vector["exp_sha"], vector["chal"])
    key.delete()


def test_import_invalid_algorithm(session):
    # Algorithm must be HMAC_SHA1, HMAC_SHA256, HMAC_SHA384 or HMAC_SHA512
    with pytest.raises(ValueError):
        HmacKey.put(
            session,
            0,
            "Test PUT invalid algorithm",
            0xFFFF,
            CAPABILITY.SIGN_HMAC,
            os.urandom(64),
            ALGORITHM.RSA_PSS_SHA256,
        )
