# Copyright 2015 Sean Dague
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import ConfigParser

ROOT_DIR = os.environ["HOME"] + "/.imaway"
CONF = ROOT_DIR + "/imaway.conf"


def _ensure_conf_dir():
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)


class Config(object):
    """Config wrapper

    Moving the config handling out of the main code logic lets us do
    things like build base config files and not explode in new
    environments.

    """
    warnlimit = 8
    infolimit = 7

    def __init__(self):
        super(Config, self).__init__()
        _ensure_conf_dir()
        config = ConfigParser.ConfigParser()
        try:
            config.read(CONF)
            self.warnlimit = config.getint('limits', 'warn')
            self.infolimit = config.getint('limits', 'info')
        except ConfigParser.NoSectionError:
            config.add_section('limits')
            config.set('limits', 'warn', self.warnlimit)
            config.set('limits', 'info', self.infolimit)
            with open(CONF, 'w') as f:
                config.write(f)
