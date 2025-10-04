from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp
from ekranlar.ilkpencere import İlkPencere
from ekranlar.ikincipencere import SecondScreen


class MyScreenManager(ScreenManager):
    pass
class TARİFApp(MDApp):
    def build(self):
       

        sm = MyScreenManager(transition=FadeTransition())  
        sm.add_widget(İlkPencere(name="first"))
        sm.add_widget(SecondScreen(name="second"))
        return sm      
if __name__ == "__main__":
    TARİFApp().run()

