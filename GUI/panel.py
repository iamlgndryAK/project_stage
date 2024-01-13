from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label

class SimpleTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super(SimpleTabbedPanel, self).__init__(**kwargs)

        # Create tabs
        tab1 = TabbedPanelItem(text='Tab 1')
        tab2 = TabbedPanelItem(text='Tab 2')

        # Add content to each tab
        tab1.add_widget(Label(text='Content of Tab 1'))
        tab2.add_widget(Label(text='Content of Tab 2'))

        # Add tabs to the tab panel
        self.add_widget(tab1)
        self.add_widget(tab2)

class SimpleTabApp(App):
    def build(self):
        return SimpleTabbedPanel()

if __name__ == '__main__':
    SimpleTabApp().run()
