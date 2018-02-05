#!/usr/bin/env python
"""
 SlipStream Client
 =====
 Copyright (C) 2018 SixSq Sarl (sixsq.com)
 =====
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from slipstream.command.CloudClientCommand import main
from slipstream.command.TerminateInstancesCommand import TerminateInstancesCommand
from slipstream_docker.DockerCommand import DockerCommand
from slipstream.ConfigHolder import ConfigHolder
from slipstream.NodeDecorator import KEY_RUN_CATEGORY


class DockerTerminateInstances(TerminateInstancesCommand, DockerCommand):

    INSTANCES_NAMESPACE = "instance-namespace"

    def _set_command_specific_options(self, parser):
        parser.add_option('--' + self.INSTANCE_IDS_KEY, dest=self.INSTANCE_IDS_KEY,
                          help='Instance ID (can be used multiple times)',
                          action='append', default=[], metavar='ID')
        parser.add_option('--' + self.INSTANCES_IDS_FILE_KEY, dest=self.INSTANCES_IDS_FILE_KEY,
                          help='File containing a list of instance ids (one per line)',
                          default=None, metavar='FILE')
        parser.add_option('--' + self.INSTANCES_NAMESPACE, dest=self.INSTANCES_NAMESPACE,
                          help='Namespace where the instances are',
                          default=[], metavar='NAMESPACE')

    def do_work(self):
        ids = self.get_option(self.INSTANCE_IDS_KEY)
        ch = ConfigHolder(options={'verboseLevel': self.options.verbose and 3 or 0,
                                   'retry': False,
                                   KEY_RUN_CATEGORY: ''},
                          context={'foo': 'bar'})
        cc = self.get_connector_class()(ch)

        # pylint: disable=protected-access
        cc._initialization(self.user_info, **self.get_initialization_extra_kwargs())

        fname = self.get_option(self.INSTANCES_IDS_FILE_KEY)
        if fname:
            with open(fname) as f:
                ids += f.read().splitlines()

        if cc.has_capability(cc.CAPABILITY_VAPP):
            cc.stop_vapps_by_ids(ids, self.get_option(self.INSTANCES_NAMESPACE))
        else:
            cc._stop_instances_in_namespace(ids, self.get_option(self.INSTANCES_NAMESPACE))

    def __init__(self):
        super(DockerTerminateInstances, self).__init__()


if __name__ == "__main__":
    main(DockerTerminateInstances)
