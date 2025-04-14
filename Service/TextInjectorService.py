

class TextInjectorService:
    _text_widget = None  # Static/class-level reference

    @classmethod
    def init(cls, text_widget):
        cls._text_widget = text_widget

    @classmethod
    def write(cls, text):
        if cls._text_widget is not None:
            cls._text_widget.insert("end", text + "\n")
            cls._text_widget.see("end")
        else:
            print("TextInjectorService not initialized with a widget.")
