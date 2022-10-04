from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup


#Window.size = (350, 600)

#class FirstWindow(Screen):
    #pass

#class SecondWindow(Screen):
    #pass

#class MyScreenManager(ScreenManager):
    #pass
    
    
class MyPopup(Popup):
    pass
    

        
class MyApp(MDApp):
    
    def on_start(self):
        #box =BoxLayout()
        #box.orientation="vertical"
        #box.add_widget(Label(text=""))
        #box.add_widget(TextInput(hint_text="enter username"))
        #box.add_widget(TextInput(hint_text="enter password"))
        #box.add_widget(Button(text="login"))
        #pop = Popup(
        #    auto_dismiss=False,
        #    title="welcome to login screen",
        #   size_hint = (0.5,0.3),
        #   pos_hint = {"center_x": 0.5, "center_y": 0.2},
        #   content = box
        #)
        #pop.open()
        pop = MyPopup()
        pop.open()
        return super().on_start()
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_file("login_ui.kv")
    
    
    def clear(self):
        self.root.ids.username.text = ""
        self.root.ids.password.text = ""
        self.root.ids.result.text = "Welcome!"
        

    
if __name__=="__main__":
    MyApp().run()
    
    