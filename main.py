"""
Name:Kenzin Igor
Date:20/05/2021
Brief Project Description:Reading Tracker
GitHub URL:https://github.com/JCUS-CP1404/assignment-2-reading-tracker-igor5514
"""
# Create your main program in this file, using the ReadingTrackerApp class

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty

from bookcollection import BookCollection
from book import Book


# Constants for work with files
FILENAME = 'books.csv'


class MainScreen(Screen):
    """Base screen."""
    def __init__(self, books=None, **kwargs):
        super().__init__(**kwargs)
        self.books = books
        self.main_box = None

    def on_enter(self):
        # Basic box
        self.main_box = MainBox(self.books)
        self.add_widget(self.main_box)


class BookButton(Button):
    """A button with a link to a specific book."""
    def __init__(self, book, top_label, warn_label, **kwargs):
        super().__init__(**kwargs)
        self.book = book
        self.top_label = top_label
        self.warn_label = warn_label
        self.set_color()
        self.text = str(book)

    def build(self):
        return self

    def set_color(self):
        """Setting the button color depending on the need / completion of reading"""
        self.background_color = 'white' if self.book.is_completed else 'aqua'

    def on_press(self):
        """Handling a book button click"""
        if self.book.is_completed:
            self.book.mark_required()
        else:
            self.book.mark_completed()
        self.set_color()
        self.text = str(self.book)
        self.top_label.set_label_text()
        text = 'You {} \'{}\'.{}'.format(
            'completed' if self.book.is_completed else 'need to read',
            self.book.title,
            (' Great job!' if self.book.is_completed else ' Get started!') if self.book.is_long() else ''
        )
        self.warn_label.set_label_text(text)


class BookLabel(Label):
    """Base Label Class"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        return self


class HeadLabel(BookLabel):
    """Top inscription."""
    def __init__(self, collection=None, **kwargs):
        super().__init__(**kwargs)
        self.collection = collection

    def set_label_text(self):
        """Displays the number of pages required to read"""
        self.text = 'Pages to read: {}'.format(self.collection.get_required_pages())

class WarningLabel(BookLabel):
    """Bottom information label"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_label_text('Welcome to the Reading Tracker 2.0!')
        self.warn = False

    def set_label_text(self, text, warn=False):
        """Sets the text and color of the label"""
        self.text = text
        self.warn = warn
        self.opacity = .8
        if self.warn:
            self.color = 'darksalmon'
        else:
            self.color = 'lightgreen'
        self.on_size()

    def on_size(self, *args):
        """Sets the background color of the label"""
        self.canvas.before.clear()
        if hasattr(self, 'warn'):
            color = (.8, 0, 0) if self.warn else (0, .5, 0)
        else:
            color = (0, .5, 0)
        with self.canvas.before:
            Color(*color, 0.25)
            Rectangle(pos=self.pos, size=self.size)


class MainBox(BoxLayout):
    """Base page layout class"""
    # Links to parts of the page layout that are set in the kv file
    spinner = ObjectProperty(None)
    maingrid = ObjectProperty(None)
    recycle = ObjectProperty(None)
    headlabel = ObjectProperty(None)
    warnlabel = ObjectProperty(None)

    def __init__(self, books=None, **kwargs):
        super().__init__(**kwargs)
        self.books = books
        self.init_grid()
        #Markers for defining the internal name of an object
        self.ids_obj = dict(zip(self.ids.values(), self.ids.keys()))
        # Navigation markers on Text Input objects when tab is pressed
        self.markers = [self.ids['add_title'], self.ids['add_author'], self.ids['add_pages']]

    def init_grid(self):
        """Preliminary steps when initializing a page"""
        self.headlabel.collection = self.books
        self.headlabel.set_label_text()
        self.warnlabel.set_label_text('Welcome to the Reading Tracker 2.0!')
        self.building_grid(None, 'Author')

    def building_grid(self, instance, value):
        """Building a list of books"""
        self.books.sort(value)
        # Building a scroll window
        self.recycle.width = Window.width
        self.recycle.height = Window.height - self.headlabel.height - self.warnlabel.height
        self.maingrid.bind(
            minimum_height=self.maingrid.setter('height')
        )
        # Redrawing the list of books
        self.maingrid.clear_widgets()
        for book in self.books:
            self.maingrid.add_widget(
                BookButton(
                    book=book,
                    top_label=self.headlabel,
                    warn_label=self.warnlabel,
                    text=str(book),
                    size_hint_y=None
                )
            )

    def add_book(self, title_obj, author_obj, pages_obj):
        """Book Adding Handling"""
        title, author, pages = map(str.strip, (title_obj.text, author_obj.text, pages_obj.text))
        # Checking the correctness of input fields
        if not title or not author or not pages:
            self.warnlabel.set_label_text('All fields must be completed', True)
            return
        try:
            pages = int(pages)
        except ValueError:
            self.warnlabel.set_label_text('Please enter a valid number', True)
            return
        if pages < 1:
            self.warnlabel.set_label_text('Pages must be > 0', True)
            return
        self.warnlabel.set_label_text('You added a new book')
        self.books.add_book(Book(title, author, pages))
        self.headlabel.set_label_text()
        self.building_grid(None, self.spinner.text)
        self.clear_addfields(title_obj, author_obj, pages_obj)

    def clear_addfields(self, title, author, pages):
        """Clearing book add fields"""
        title.text = ''
        author.text = ''
        pages.text = ''

    def text_control(self, field):
        """Controlling movement through tab input fields"""
        if field.text.endswith('\t'):
            field.text = field.text[:-1]
            idx = self.markers.index(field)
            field.focus = False
            if idx == len(self.markers)-1:
                self.markers[0].focus = True
            else:
                self.markers[idx+1].focus = True


class ReadingTrackerApp(App):
    """Basic application"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.books = BookCollection()
        try:
            self.books.load_books(FILENAME, backup=True)
        except (FileNotFoundError, LookupError):
            pass

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(self.books))
        return sm

    def on_stop(self):
        """Saving an updated book list file"""
        self.books.save_books(FILENAME)
        return super().on_stop()


if __name__ == '__main__':
    ReadingTrackerApp().run()
