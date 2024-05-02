from frontend import layout, util
from frontend.model import Model
from argparse import ArgumentParser

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings

from json import load

def main():
    """Main function of the front end.

    The main function of the front end merely parses the command line
    arguments and calls the respective functions from the frontend
    package.

    Returns:
        int: 0 on scucess, 1 on failure
    """

    parser = ArgumentParser()

    parser.add_argument("-m", "--models", type=str, required=True,
            help="The models used that generated the report in zip format.")
    parser.add_argument("-r", "--report", type=str, required=True,
            help="The report emitted by the mlsast-prototype in JSON format.")
    parser.add_argument("-f", "--report-threshold", type=int, default=5,
                        help="Maximum number of findings to display.")
    parser.add_argument("-l", "--lower-bound", type=int, default=10,
                        help="Minimum percentage a characteristic must " \
                            + "fulfill so as to be reported.")
    parser.add_argument("-u", "--upper-bound", type=int, default=80,
                        help="Maximum percentage a characteristic may " \
                            + "fulfill so as to be reported.")
    parser.add_argument("-b", "--block-list", nargs="+",
                        help="List of models to be filtered out of the report.")
    parser.add_argument("-x", "--filter-functions", type=str, default=".*",
                        help="Regular expression for filtering functions.")
    args = parser.parse_args()

    if args.block_list is None:
        args.block_list = []

    report = util.open_report(
        args.report,
        args.lower_bound,
        args.upper_bound,
        args.block_list,
        args.filter_functions
    )

    model = Model(args.models)
    report_threshold = args.report_threshold

    _main_view = layout.MainView(report, model, report_threshold)
    _handlers = layout.Handlers(_main_view)
    _bindings = KeyBindings()

    _main_view._button_next.handler = _handlers.handler_next
    _main_view._button_prev.handler = _handlers.handler_prev
    _main_view._button_hide.handler = _handlers.handler_hide
    _main_view._button_save.handler = _handlers.handler_save
    _main_view._button_quit.handler = _handlers.handler_quit

    @_bindings.add("p")
    def prev_(event):
        _handlers.handler_prev()

    @_bindings.add("n")
    def next_(event):
        _handlers.handler_next()

    @_bindings.add("h")
    def hide_(event):
        _handlers.handler_hide()

    @_bindings.add("s")
    def save_(event):
        _handlers.handler_save()

    @_bindings.add("q")
    def exit_(event):
        _handlers.handler_quit()

    @_bindings.add("c-c")
    def exit_(event):
        event.app.exit()

    _app = Application(key_bindings=_bindings, layout=_main_view.get_layout(),
            mouse_support=True, full_screen=True)
    _app.run()

    return 0
if __name__ == "__main__":
    main()
