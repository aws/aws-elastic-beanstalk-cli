# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from cement.core import controller, handler

from ..core import io
from ..lib import aws
from ..operations import commonops


class CompleterController(controller.CementBaseController):
    class Meta:
        label = 'completer'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'auto-completer: hidden command'
        arguments = [
            (['--cmplt'], dict(help='command list so far')),
        ]
        hide = True

    @controller.expose(hide=True)
    def default(self):
        """
        Creates a space separated list of possible completions.
        We actually do not need to calculate the completions. We can simply
        just generate a list of ALL possibilities, and then the bash completer
         module is smart enough to filter out the ones that don't match.

         Results must be printed through stdin for the completer module
         to read then.
        """

        commands = self.app.pargs.cmplt.strip('"')

        # Get commands, filter out last one
        commands = commands.split(' ')
        word_so_far = commands[-1]
        commands = commands[0:-1]
        commands = list(filter(lambda x: len(x) > 0, commands))

        #Get the list of controllers
        self.controllers = handler.list('controller')
        self._filter_controllers()

        ctrlr = self._get_desired_controller(commands)

        if not ctrlr:
            return  # command entered so far is invalid, we dont need to
                    ##   worry about completion

        if word_so_far.startswith('--'):
            # Get all base option flags
            self.complete_options(ctrlr)
        else:
            if ctrlr == self.base_controller:
                # Get standard command list
                io.echo(*[c.Meta.label for c in self.controllers
                          if not hasattr(c.Meta, 'stacked_type')])
            else:
                # A command has been provided. Complete at a deeper level

                ctrlr = ctrlr()  # Instantiate so we can read all arguments

                if not hasattr(ctrlr, 'complete_command'):
                    return  # Controller does not support completion

                try:
                    #Set up aws profile just in case we need to make a service call
                    profile = commonops.get_default_profile()
                    if profile:
                        aws.set_profile(profile)
                    ctrlr.complete_command(commands)
                except:
                    #We want to swallow ALL exceptions. We can
                    ## not print any output when trying to tab-complete
                    ## because any output gets passed to the user as
                    ## completion candidates
                    ### Exceptions here are normally thrown because the service
                    ### can not be contacted for things such as environment
                    ### list and solution stack list. Typically, credentials
                    ### are not set up yet
                    pass

    def complete_options(self, controller):
        # Get all base options (excluding the one for this controller)
        base_options = [c.option_strings[-1] for c in self.app.args._actions if
                        c.option_strings[-1] != '--cmplt']

        controller_options = [o[0][-1] for o in controller()._meta.arguments if
                              o[0][-1].startswith('--')]

        io.echo(*base_options + controller_options)

    def _get_desired_controller(self, commands):
        if len(commands) < 1:
            return self.base_controller
        else:
            return next((c for c in self.controllers if
                         c.Meta.label == commands[0]), None)

    def _filter_controllers(self):
        #filter out unwanted controllers
        self.base_controller = next((c for c in self.controllers if
                                     c.Meta.label == 'base'), None)
        self.controllers = [c for c in self.controllers if
                            c.Meta.label != 'base' and
                            c.Meta.label != 'completer']