from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.widgets import Checkbox as Box


class Checkbox(Box):
    def __init__(self, text: AnyFormattedText = "",
                 checked: bool = False, onclick: callable = None) -> None:
        self.onclick = onclick
        super().__init__(text, checked)
        
    def _handle_enter(self) -> None:
        if self.onclick is not None:
            self.onclick()

        if self.multiple_selection:
            val = self.values[self._selected_index][0]
            if val in self.current_values:
                self.current_values.remove(val)
            else:
                self.current_values.append(val)
        else:
            self.current_value = self.values[self._selected_index][0]
