from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock


Builder.load_string(""" 
<Button>
    font_size: 60
    background_normal: ""
    background_color: (1, 0, 0, 1)


<Grid>
    GridLayout:
        id: main_grid
        cols: 1
        size: root.width, root.height

        GridLayout:
            id: top_grid
            cols: 1

            Label:
                id: progress_label
                text: ""
                size_hint: (1, 0.3)

            ProgressBar:
                id: loading_bar
                min: 0
                max: 100

                value: 25


            Button:

                text: "Submit"
""")


class Grid(Widget):

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        Clock.schedule_interval(self.update_label, 0.2)

        animation = Animation(value=50, duration=4)
        animation = animation + Animation(value=100, duration=0.8)
        animation.start(self.ids.loading_bar)

    def update_label(self, error):
        self.ids.progress_label.text = f"{str(round(self.ids.loading_bar.value))}%"


class Root(App):
    def build(self):
        Window.clearcolor = (0.12, 0.8, 0.3, 1)
        return Grid()


if __name__ == "__main__":
    app = Root()
    app.run()
