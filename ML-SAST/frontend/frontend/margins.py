from prompt_toolkit.layout.controls import UIContent
from prompt_toolkit.layout.margins import Margin
from prompt_toolkit.formatted_text import StyleAndTextTuples

from typing import TYPE_CHECKING, Callable

class DeltaData:
    def __init__(self, line_dict={}, hl_lines=[]):
        self.line_dict = line_dict
        self.hl_lines = hl_lines

class DeltaMargin(Margin):
    """
    Margin that displays the line numbers and allows for highlighting
    a given set of line numbers.
    """

    def __init__(self, data: DeltaData, line_offset=1) -> None:
        self.data = data
        self.line_offset = line_offset
        
    def update_data(self, data: DeltaData):
        self.data = data

    def get_width(self, get_ui_content: Callable[[], UIContent]) -> int:
        line_count = get_ui_content().line_count
        return max(5, len("%s" % line_count) + 1)

    def create_margin(
        self, window_render_info: "WindowRenderInfo", width: int, height: int
    ) -> StyleAndTextTuples:

        style = "class:line-number"
        style_current = "class:line-number.current"
        style_hl = "bg:ansired"
        
        line_dict = self.data.line_dict
        hl_lines = self.data.hl_lines

        # Get current line number.
        current_lineno = window_render_info.ui_content.cursor_position.y

        # Construct margin.
        result: StyleAndTextTuples = []
        last_lineno = None

        for y, lineno in enumerate(window_render_info.displayed_lines):
            
            # This check is not sufficient if the indeces in the json report are
            # garbage, but it is faster than to check the indece against every
            # possible value in the dictionary for it's presence.
            if lineno + self.line_offset > len(line_dict):
                pass
            else:
                realno = line_dict[lineno + self.line_offset]
            
                if realno != last_lineno:
                    if realno is None:
                        pass
                    elif line_dict.get(lineno+1) in hl_lines:
                        result.append(
                            (style_hl, ("%i " % (realno)).rjust(width))
                        )
                    elif lineno == current_lineno:
                        result.append(
                            (style_current, ("%i " % (realno)).rjust(width))
                        )
                    else:
                        result.append((style, ("%i " % (realno)).rjust(width)))

            last_lineno = realno
            result.append(("", "\n"))

        return result
