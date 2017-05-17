#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import uuid

from openstackclient.tests.functional.volume.v2 import common


class TransferRequestTests(common.BaseVolumeTests):
    """Functional tests for transfer request. """

    NAME = uuid.uuid4().hex
    VOLUME_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(TransferRequestTests, cls).setUpClass()

        cmd_output = json.loads(cls.openstack(
            'volume create -f json --size 1 ' + cls.VOLUME_NAME))
        cls.assertOutput(cls.VOLUME_NAME, cmd_output['name'])

        cmd_output = json.loads(cls.openstack(
            'volume transfer request create -f json ' +
            cls.VOLUME_NAME +
            ' --name ' + cls.NAME))
        cls.assertOutput(cls.NAME, cmd_output['name'])

    @classmethod
    def tearDownClass(cls):
        raw_output_transfer = cls.openstack(
            'volume transfer request delete ' + cls.NAME)
        raw_output_volume = cls.openstack(
            'volume delete ' + cls.VOLUME_NAME)
        cls.assertOutput('', raw_output_transfer)
        cls.assertOutput('', raw_output_volume)

    def test_volume_transfer_request_accept(self):
        volume_name = uuid.uuid4().hex
        name = uuid.uuid4().hex

        # create a volume
        cmd_output = json.loads(self.openstack(
            'volume create -f json --size 1 ' + volume_name))
        self.assertEqual(volume_name, cmd_output['name'])

        # create volume transfer request for the volume
        # and get the auth_key of the new transfer request
        cmd_output = json.loads(self.openstack(
            'volume transfer request create -f json ' +
            volume_name +
            ' --name ' + name))
        auth_key = cmd_output['auth_key']
        self.assertTrue(auth_key)

        # accept the volume transfer request
        cmd_output = json.loads(self.openstack(
            'volume transfer request accept -f json ' +
            name + ' ' +
            '--auth-key ' + auth_key
        ))
        self.assertEqual(name, cmd_output['name'])

        # the volume transfer will be removed by default after accepted
        # so just need to delete the volume here
        raw_output = self.openstack(
            'volume delete ' + volume_name)
        self.assertEqual('', raw_output)

    def test_volume_transfer_request_list(self):
        cmd_output = json.loads(self.openstack(
            'volume transfer request list -f json'))
        self.assertIn(self.NAME, [req['Name'] for req in cmd_output])

    def test_volume_transfer_request_show(self):
        cmd_output = json.loads(self.openstack(
            'volume transfer request show -f json ' + self.NAME))
        self.assertEqual(self.NAME, cmd_output['name'])
