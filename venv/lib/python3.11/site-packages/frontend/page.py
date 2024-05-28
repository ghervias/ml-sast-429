from itertools import islice

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.widgets import Frame
from pygments.lexers.c_cpp import CppLexer
from pygments.styles import get_style_by_name

from . import margins, util
from .checkbox import Checkbox
from .model import Model

style = style_from_pygments_cls(get_style_by_name('monokai'))
lexer = PygmentsLexer(CppLexer)

def make_stat(title: str, percent: float, title_width: int, width=50,
              onclick: callable = None) -> Frame:
    """Builds a defect characteristics container.

    Args:
        title (str): The model that raised an alarm.
        percent (float): Probability of the alarm being a TP.
        width (int, optional): Width of the container. Defaults to 50.

    Returns:
        Frame: The defect characteristics container.
    """

    # Format string + title length = info length
    info_width = 10 + title_width
    info = f" {title : <9}{percent: 3.1f}% "

    # Total width - radio button - percentage - title length = bar length
    bar_width = width - 3 - 10 - title_width
    bar = util.get_percent_bar(percent, bar_width)

    # Percentage bars are colored in, corresponding to their severity.
    checked = False

    # We must store the checkboxes separately or else they cannot be retrieved
    # anymore from the VSplit children (or at leas I failed to do so).
    check_box = Checkbox(checked=checked, onclick=onclick)

    # We return tuples of the VSplit and the corresponding checkbox
    return VSplit([
            Window(content=FormattedTextControl(info), width=info_width),
            Window(content=FormattedTextControl(bar), width=bar_width),
            check_box
    ], width=width), check_box

def make_code(code: str, line_dict: dict, hl_lines: list):
    """Function for generating a code view for the left hand sinde of
    the laylout.

    Args:
        code (str): A multiline string containing the raw source code.
        line_dict (dict): A dictionary mapping the line numbers of the
            raw (truncated) code to its actual line numbers.
        hl_lines (list): The lines to be highlighted in terms of the actual
            lines numbers.

    Returns:
        Window: A window containing all elements, ready for rendering.
    """
    code_buffer = Buffer(name="code_view", read_only=True)
    delta_data = margins.DeltaData()
    delta_data.hl_lines = hl_lines
    delta_data.line_dict = line_dict

    code_view = Window(content=BufferControl(buffer=code_buffer,
                            lexer=lexer,
                            focus_on_click=True),
                    left_margins=[margins.DeltaMargin(delta_data)],
                    right_margins=[ScrollbarMargin(display_arrows=True)],
                    wrap_lines=True
    )

    code = Document(text=code, cursor_position=0)
    code_buffer.set_document(code, bypass_readonly=True)

    return code_view

class Page():
    """Class holding all context data for each layout to be drawn. A page not
    only holds all the elements to be rendered to the screen, but also saves the
    results, i.e., the selections made by the user.
    """

    def __init__(self, index: int, stats: dict, code: str, line_dict: list,
            hl_lines: list, title_width: int, code_path: list,
            model: Model, report_threshold: int,
            checkbox_handler: callable) -> None:
        """Constructor for the Page class.

        Args:
            index (int): The index of the page.
            stats (dict): The stats from the run, a dictionary where the keys
                are the titles of the models and the values are floats
                representative of the achieved score for the current path.
            code (str): The code, a string containg the deltas around the nodes
                of the path.
            line_dict (list): The dictionary containing a mapping from the line
                numbers from the code sring onto the line numbers from the
                actual source code files that have been retrieved from the debug
                information.
            hl_lines (list): A list of integers representing the lines to be
                highlighted.
            title_width (int): The width of the longest model name across all
                pages (hence why it needs to be determined elsewhere), which is
                necessary to align the stat bars correctly.
            code_path (list): The original extracted path, a sequence of
                nodes.
            model (Model): The model to be used for eventual updates.
            report_threshold (int): Number of detected models to display
            for each finding
            checkbox_handler (callable): Function that is called if a checkbox
            in the stats window is clicked.
        """

        self.index = index
        self.code = code
        self.line_dict = line_dict
        self.hl_lines = hl_lines
        self.code_path = code_path
        self.use = False
        self.changed = False
        self.checkbox_handler = checkbox_handler

        self.model = model

        # get first n stats
        stats_filtered = dict(islice(stats.items(),
            report_threshold))

        # Generate stats using make_stat(), which returns the VSplit as well as
        # its corresponding checkbox as a tuple.
        self.stats = {t: make_stat(t, p, title_width, onclick=self.onclick) for t, p \
            in stats_filtered.items()}

        # Retrieve the checkboxes from the stats generated above.
        self.selection = {t: s[1] for t, s in self.stats.items()}

        # Remove tuples from the stats dictionary, so that they just contain the
        # title of the defect from the model and the VSplit.
        self.stats = {t: s[0] for t, s in self.stats.items()}

        # Saves the state of the checkboxes to detected changes. Used for making
        # updates to the save state indicator.
        self.box_state = [box.checked for box in self.selection.values()]

        # Determine the maximum width of all titles in the stats.
        self.title_width = max([len(t) for t, p in stats.items()])

    def onclick(self):
        self.changed = True

        if self.checkbox_handler is not None:
            self.checkbox_handler()

    def get_model_selection(self):
        """Retrieves the checkbox status for each of the models where a checked
        box means the model must be adapted and an unchecked one that the model
        should be kept as is.

        Returns:
            dict: A dictionary containing the model name and the selection
            status.
        """
        selection = {}

        for model, box in self.selection.items():
            selection.update({model: box.checked})

        return selection

    def has_changed(self) -> bool:
        """Determines whether the model selection has changed or not.

        Returns:
            bool: True if changed else False.
        """
        return self.changed

    def mark_saved(self):
        """Mark changes as saved.
        """

        self.box_state = [box.checked for box in self.selection.values()]

