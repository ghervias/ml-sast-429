from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.widgets import Button, Frame
from pygments.lexers.c_cpp import CppLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.application import get_app

from . import margins, page
from .model import Model

style = style_from_pygments_cls(get_style_by_name('monokai'))
lexer = PygmentsLexer(CppLexer)

class MainView():
    """The MainView class contains all visible elements of the user interface.
    It must be initiliazed first by calling its constructor and then assigning
    all necessary button handlers and keybindings.
    """
    def __init__(self, data: list, model: Model, report_threshold: int,
                 checkbox_handler: callable = None) -> None:
        """The initializer of the main view. The data contains the raw json data
        of the reports. Each report must contain the following fields:

        "code" (str): The source code as deltas around the affected code lines
            from the paths.
        "line_dict" (dict): A dictionary, mapping all lines of the code string
            onto the line numbers to be shown in the UI.
        "hl_lines" (list[int]): A list of integers of the mapped lines to be
            highlighted by the ui.
        "stats" (list[tuple]): A list of tuples where the first element of each
            tuple is the name of the model (str) and the second element is the
            score (float) the model yielded for the current path.

        Args:
            data (list): A list of reports as decribed.
            model (Model): The models to be used for eventual adaptations.
            report_threshold (int): Number of detected models to display.
            for each finding
        """

        self.page_index = 0
        self.pages = []

        # The progress indicator shown at the bottom of the UI.
        self._progress_view = Window(content=FormattedTextControl(
                    text=""),
                dont_extend_width=True)

         # The save indicator shown at the bottom of the UI.
        self._save_view = Window(content=FormattedTextControl(
                    text=""),
                dont_extend_width=True)

        # The code buffer that displays the highlighted code corresponding to
        # the paths.
        self._code_buffer = Buffer(name="code_view", read_only=True)

        # A data container for the line number margin to the left of the code.
        self._delta_data = margins.DeltaData()

        # The root container of the statistics. Statistics are exchanged along
        # with the code on each page flip.
        self._stats_view = HSplit([])

        # Definitions of the UI buttons shown at the bottom. We must assign the
        # handlers later on, since we need a reference to the ui elements that
        # have not yet been declared.
        self._button_hide = Button(text="hide (h)", left_symbol=" [ ",
                right_symbol=" ] ",
                width=14)
        self._button_prev = Button(text="prev (p)", left_symbol=" [ ",
                right_symbol=" ] ",
                width=14)
        self._button_next = Button(text="next (n)", left_symbol=" [ ",
                right_symbol=" ] ",
                width=14)
        self._button_save = Button(text="save and quit (s)", left_symbol=" [ ",
                right_symbol=" ] ",
                width=23)
        self._button_quit = Button(text="quit w/o saving (q)", left_symbol=" [ ",
                right_symbol=" ] ",
                width=24)

        # The root layout container of the user interface, containing all static
        # elements that need not be updated.
        self._root_container = HSplit([
            VSplit([
                Frame(
                    Window(content=BufferControl(buffer=self._code_buffer,
                                    lexer=lexer,
                                    focus_on_click=True),
                            left_margins=[margins.DeltaMargin(self._delta_data)],
                            right_margins=[ScrollbarMargin()],
                            wrap_lines=True),

                    title="Affected Path"
                ),
                Frame(
                    self._stats_view,
                    title="Defect Characteristics"
                )
            ]),
            VSplit([
                self._progress_view,
                self._save_view,
                self._button_hide,
                self._button_prev,
                self._button_next,
                self._button_save,
                self._button_quit
            ])
        ])

        # Build the layout
        self._layout = Layout(self._root_container)

        # In order to construct the pages we must first determine the length of
        # the longest model name for alignment purposes.
        title_width = 0
        for index, report in enumerate(data):
            width = max([len(t) for t, p in report.get("stats").items()])
            title_width = max(width, title_width)

        # Then we can construct the individual pages.
        for index, report in enumerate(data):
            self.pages.append(
                page.Page(index, report.get("stats"), report.get("code"),
                        report.get("line_dict"), report.get("hl_lines"),
                        title_width, report.get("path"), model,
                        report_threshold, checkbox_handler=self.checkbox_click)
            )

        if not self.pages:
            raise Exception("There are no paths to be shown! " \
                    "Please ensure no unsatisfiable filters are used "
                    "and that there are indeed reports to begin with.")


        # We set the page index to the first page and update the ui for the
        # first time.
        page_index = 0
        self.update_progress((page_index, len(self.pages)), False)
        self.update_stats(self.pages[page_index])
        self.update_code(self.pages[page_index])
        self.update_save("saved")

    def get_layout(self) -> Layout:
        """Getter for the layout.

        Returns:
            Layout: returns the layout object.
        """
        return self._layout

    def checkbox_click(self):
        # Update status information.
        self.update_progress((self.page_index,
                len(self.pages)),
                    self.pages[self.page_index].use)

        # Update save state indicator
        self.update_save("changed")

    def update_code(self, page: page.Page):
        """Updates the code view provided a page. Updates to the code should only
        be performed in conjunction with an update to the stats as well as the
        progress indicator.

        Args:
            page (page.Page): The page to be displayed.
        """

        # In order to display the code, we must first construct a Document
        # object of the code before passing it to the code buffer. The we must
        # also set the highlighted lines and the lines to be mapped for the line
        # number margin.
        code = Document(text=page.code, cursor_position=0)
        self._code_buffer.set_document(code, bypass_readonly=True)

        self._delta_data.line_dict = page.line_dict
        self._delta_data.hl_lines = page.hl_lines

    def update_stats(self, page: page.Page):
        """Updates the stats view, given a page. Updates to the stats should
        only be performed in conjunction to updates to the code view and the
        progress indicator.

        Args:
            page (page.Page): The page to be displayed.
        """

        self._stats_view.children = page.stats.values()

    def update_progress(self, progress: tuple, used: bool):
        """Updates the progress indicator to reflect the current page index.

        Args:
            progress (tuple): A tuple containing the current page as the first
            element and the the total number of pages as the second element.
        """

        self._progress_view.content.text = \
            f"[ Report {progress[0]+1} / {progress[1]} ] "

    def update_save(self, status: str):
        """Updates the save indicator where True is saved and False is unsaved.

        Args:
            saved (bool): Sets save indicator: True -> saved, False -> unsaved.
        """
        if status == "saved":
            self._save_view.content.text = "[  saved  ]"
            self._save_view.style = "fg:ansigreen"
        elif status == "saving":
            self._save_view.content.text = "[  saving...  ]"
            self._save_view.style = "fg:ansiyellow"
        elif status == "changed":
            self._save_view.content.text = "[ changed ]"
            self._save_view.style = "fg:ansired"
        else:
            raise AssertionError("Wrong argument supplied: %s", status)




class Handlers():
    """Class containing all handlers that are then called by either the buttons
    or the keybindings. These must be kept in a separate class that is provided
    with the MainView object being displayed, since we need to declare some
    visual elements first that we need the references to.
    """

    def __init__(self, view: MainView) -> None:
        """Initializes the handlers given the MainView object.

        Args:
            view (MainView): The MainView object being displayed.
        """

        self.view = view

    def handler_next(self):
        """Handler managing forward page flips. It updates the page index and
        performs the required changes to the UI. If we are at the first page
        already the procedure does nothing but return.
        """
        if self.view.page_index < len(self.view.pages) - 1:
            self.view.page_index = self.view.page_index + 1

            self.view.update_progress((self.view.page_index,
                    len(self.view.pages)),
                    self.view.pages[self.view.page_index].use)
            self.view.update_stats(self.view.pages[self.view.page_index])
            self.view.update_code(self.view.pages[self.view.page_index])

            if (self.view.pages[self.view.page_index - 1].has_changed()):
                self.view.update_save("changed")

    def handler_prev(self):
        """Handler managing backward page flips. It updates the page index and
        performs the required changes to the UI. If we are at the first page
        already the procedure does nothing but return.
        """
        if self.view.page_index > 0:
            self.view.page_index = self.view.page_index - 1

            self.view.update_progress((self.view.page_index,
                        len(self.view.pages)),
                    self.view.pages[self.view.page_index].use)
            self.view.update_stats(self.view.pages[self.view.page_index])
            self.view.update_code(self.view.pages[self.view.page_index])

            if (self.view.pages[self.view.page_index + 1].has_changed()):
                self.view.update_save("saved")

    def handler_hide(self):
        """Performs the deletion of a page. A page in only deleted in main
        memory but not from disk, i.e., the report file is left untouched by
        this procedure. It thus only serves usabiltiy purposes, hiding unwanted
        paths during a single session. Deletions are hence not persisted either.
        """

        # If there is just a single path in the pages, there is nothing we can
        # do that would make sense, so we just return.
        if len(self.view.pages) == 1:
            return

        # Actual deletion operation.
        self.view.pages.pop(self.view.page_index)

        # If the last item is reached and there are two elements,
        # we step backwards.
        if self.view.page_index == len(self.view.pages) - 1:
            self.view.page_index - 1

        # Otherwise we must move forward.
        else:
            self.view.page_index + 1

        # Finally we must update the view to reflect the changes.
        self.view.update_progress((self.view.page_index,
                len(self.view.pages)),
                    self.view.pages[self.view.page_index].use)
        self.view.update_stats(self.view.pages[self.view.page_index])
        self.view.update_code(self.view.pages[self.view.page_index])

    def handler_save(self):
        """Handler initiating the model adaptations. This handler is called
        when the save button is actuated.
        """

        selections = []

        for page in self.view.pages:
            boxes = page.selection.items()
            box_checked = [list(boxes)[x][1].checked for x in range(len(boxes))]
            if any(box_checked):
                selection = page.get_model_selection()

                for model, use in selection.items():
                    if use:
                        selections.append((model, page.code_path))


        self.view.update_save("saving")
        page.model.persist(selections)
        self.view.update_save("saved")

        get_app().exit()

    def handler_quit(self):
        """ Handler that simply exits the application.
        """
        get_app().exit()
