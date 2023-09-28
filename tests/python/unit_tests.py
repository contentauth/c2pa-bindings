# Copyright 2023 Adobe. All rights reserved.
# This file is licensed to you under the Apache License,
# Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# or the MIT license (http://opensource.org/licenses/MIT),
# at your option.

# Unless required by applicable law or agreed to in writing,
# this software is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR REPRESENTATIONS OF ANY KIND, either express or
# implied. See the LICENSE-MIT and LICENSE-APACHE files for the
# specific language governing permissions and limitations under
# each license.import unittest

import unittest
from unittest.mock import mock_open, patch
import c2pa_api
from c2pa_api import c2pa
import os
PROJECT_PATH = os.getcwd()

testPath = os.path.join(PROJECT_PATH, "tests", "fixtures", "C.jpg")

class TestC2paSdk(unittest.TestCase):

    def test_version(self):
        self.assertIn("c2pa-rs/",c2pa_api.c2pa.version())

    def test_supported_extensions(self):
        self.assertIn("jpeg",c2pa_api.c2pa.supported_extensions())


class TestManifestStoreReader(unittest.TestCase):

    def test_normal_read(self):
        with open(testPath, "rb") as file:
            manifestStore = c2pa_api.ManifestStoreReader("image/jpeg",file)
            json = manifestStore.read()
            self.assertIn("C.jpg", json)

    def test_normal_read_and_parse(self):
        with open(testPath, "rb") as file:
            manifestStore = c2pa_api.ManifestStoreReader("image/jpeg",file)
            manifestStore.read()
            json = manifestStore.json()
            manifest_store = c2pa_api.ManifestStore.from_json(json)
            title= manifest_store.manifests[manifest_store.activeManifest].title
            self.assertEqual(title, "C.jpg")

    def test_json_decode_err(self):
        with self.assertRaises(c2pa_api.json.decoder.JSONDecodeError):
            manifest_store = c2pa_api.ManifestStore.from_json("foo")

    def test_reader_bad_format(self):
        with self.assertRaises(c2pa_api.c2pa.StreamError.Other):
            with open(testPath, "rb") as file:
                manifestStore = c2pa_api.ManifestStoreReader("badFormat",file)
                json = manifestStore.read()

class TestManifestBuilder(unittest.TestCase):
    # Define a manifest as a dictionary
    manifestDefinition = {
        "claim_generator": "python_test",
        "claim_generator_info": [{
            "name": "python_test",
            "version": "0.0.1",
        }],
        "format": "image/jpeg",
        "title": "Python Test Image",
        "ingredients": [],
        "assertions": [
            {   'label': 'stds.schema-org.CreativeWork',
                'data': {
                    '@context': 'http://schema.org/',
                    '@type': 'CreativeWork',
                    'author': [
                        {   '@type': 'Person',
                            'name': 'Gavin Peacock'
                        }
                    ]
                },
                'kind': 'Json'
            }
        ]
    }

    def sign_ps256(data: bytes) -> bytes:
        return c2pa_api.sign_ps256(data, "tests/fixtures/ps256.pem")

    # load the public keys from a pem file
    pemFile = os.path.join(PROJECT_PATH,"tests","fixtures","ps256.pub")
    certs = open(pemFile,"rb").read()

    # Create a local signer from a certificate pem file
    signer = c2pa_api.LocalSigner.from_settings(sign_ps256, "ps256", certs, "http://timestamp.digicert.com")

    def test_normal_build(self):
        with open(testPath, "rb") as file:
            settings = c2pa_api.c2pa.ManifestBuilderSettings("python-generator") 
            builder = c2pa_api.ManifestBuilder(settings, TestManifestBuilder.signer, TestManifestBuilder.manifestDefinition)
            json = builder.sign()
            self.assertIn("C.jpg", json)



if __name__ == '__main__':
    unittest.main()