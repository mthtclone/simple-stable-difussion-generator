class ConsoleRedirect:

    def __init__(self, widget):
        self.widget = widget

    def write(self, text):

        if text.strip():
            self.widget.write_log(text)

    def flush(self):
        pass