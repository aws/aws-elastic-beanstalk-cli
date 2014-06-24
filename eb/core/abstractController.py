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

from cement.core import foundation, controller, handler

class AbstractBaseController(controller.CementBaseController):
    """
    This is an abstract base class that is useless on its own, but used
    by other classes to sub-class from and to share common commands and
    arguments.

    """
    class Meta:
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            ( ['-f', '--foo'], dict(help='notorious foo option')),
            ]

    def _setup(self, base_app):
        """
        Add a common object that is useful in multiple sub-classed
        controllers.

        """
        super(AbstractBaseController, self)._setup(base_app)
        self.my_shared_obj = dict()

    def do_command(self):
        pass

    @controller.expose(hide=True)
    def default(self):
        """
        This command will be shared within all controllers that sub-class
        from here.  It can also be overridden in the sub-class, but for
        this example we are making it dynamic.

        """
        self.do_command()