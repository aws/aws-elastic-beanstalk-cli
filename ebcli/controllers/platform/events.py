from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.operations.platformops import show_platform_events
from ebcli.resources.strings import strings, flag_text


class GenericPlatformEventsController(AbstractBaseController):
    class Meta:
        is_platform_workspace_only_command = True
        requires_directory_initialization = True
        description = strings['platformevents.info']
        arguments = [
            (['version'], dict(action='store', nargs='?', default=None, help=flag_text['platformevents.version'])),
            (['-f', '--follow'], dict(action='store_true', help=flag_text['events.follow']))
        ]

        @classmethod
        def clone(cls):
            return type('Meta', cls.__bases__, dict(cls.__dict__))

    def do_command(self):
        self.app.args.print_help()

    @classmethod
    def add_to_handler(cls, handler):
        handler.register(cls)

    def do_command(self):
        version = self.app.pargs.version
        follow = self.app.pargs.follow

        show_platform_events(follow, version)


class PlatformEventsController(GenericPlatformEventsController):
    Meta = GenericPlatformEventsController.Meta.clone()
    Meta.label = 'platform events'
    Meta.aliases = ['events']
    Meta.aliases_only = True
    Meta.stacked_on = 'platform'
    Meta.stacked_type = 'nested'
    Meta.usage = 'eb platform events <version> [options...]'


class EBPEventsController(GenericPlatformEventsController):
    Meta = GenericPlatformEventsController.Meta.clone()
    Meta.label = 'events'
    Meta.usage = 'ebp events <version> [options...]'
