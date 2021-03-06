# Copyright (C) 2016 OpenMotics BVBA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
The shutters module contains classes to track the current state of the shutters on
the master.

@author: fryckbos
"""

import time

class ShutterStatus(object):
    """ Tracks the current state of the shutters. """

    def __init__(self):
        """ Default constructor. Call init to initialize the states. """
        self.__configs = None
        self.__timestamped_states = []

    def init(self, shutter_configs, shutter_states):
        """ Initialize the states using the shutter configs and shutter states.

        :param shutter_configs: The shutter configurations.
        :type shutter_configs: List of shutter configurations (1 element per shutter module).
        :name shutter_states: The shutter states.
        :type shutter_states: List of shutter states (1 element per shutter module).
        """
        if len(shutter_configs) != len(shutter_states):
            raise ValueException("The size of the configs (%d) and states (%d) do not match " %
                                 len(shutter_configs), len(shutter_states))

        self.__configs = shutter_configs

        self.__timestamped_states = []
        for i in range(len(shutter_configs)):
            states = self.__create_states(shutter_configs[i], shutter_states[i])
            self.__timestamped_states.append(zip([ time.time() for _ in states], states))


    def __create_states(self, module_config, module_state):
        """ Create a list containing the state of one module, for example:
         ['going_up', 'going_down', 'stopped', 'stopped'].
         
         :param module_config: List of all shutter configurations for the module.
         :param module_state: byte containing 1 bit per outputs for the module.
         :returns: List of strings.
        """
        states = []
        for i in range(4):
            # updown = 0 -> output 0 = up, updown = 1 -> output 1 = up
            up_down = 0 if module_config[i]['up_down_config'] == 0 else 1

            up = (module_state >> (i * 2 + (1 - up_down))) & 0x1
            down = (module_state >> (i * 2 + up_down)) & 0x1

            if up == 1:
                states.append('going_up')
            elif down == 1:
                states.append('going_down')
            else:
                states.append('stopped')

        return states

    def handle_shutter_update(self, update):
        """ Update the status with an shutter update message. """
        now = time.time()
        module = update['module_nr']

        current_state = self.__create_states(self.__configs[module], update['status'])
        t_state = self.__timestamped_states[module]

        for i in range(4):
            if current_state[i] == t_state[i][1]:
                pass # Nothing changed.
            else:
                if current_state[i] == 'stopped':
                    if t_state[i][1] == 'going_up':
                        roll_time = 0.95 * self.__configs[module][i]['timer_up'] # 5% time slack.
                        full_run = (t_state[i][0] + roll_time <= now)

                        if full_run:
                            t_state[i] = (now, 'up')
                        else:
                            t_state[i] = (now, 'stopped')

                    elif t_state[i][1] == 'going_down':
                        roll_time = 0.95 * self.__configs[module][i]['timer_down'] # 5% time slack.
                        full_run = (t_state[i][0] + roll_time <= now)

                        if full_run:
                            t_state[i] = (now, 'down')
                        else:
                            t_state[i] = (now, 'stopped')

                    else:
                        pass # Was already stopped, nothing changed. 

                else:
                    # The new state is going_up or going_down, the old state was stopped, up or down.
                    # Set the timestamp, so when know when the shutter started going up/down.
                    t_state[i] = (now, current_state[i])

    def get_status(self):
        """ Return the list of shutters states. """
        status = []

        for states in self.__timestamped_states:
            status.extend([ state[1] for state in states ])

        return status
