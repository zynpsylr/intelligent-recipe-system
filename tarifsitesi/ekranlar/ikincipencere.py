import requests
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from baglanti import connection
from ekranlar.detayekrani import DetayEkrani

class SecondScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

       
        self.layout = FloatLayout()

        self.result_label = MDLabel(
            text="FAVORİLERİM",
            size_hint=(0.9, None),
            height=50,
            text_size=(Window.width*0.9, None),
            halign="center",
            pos_hint={"center_x": 0.5, "top": 0.95}
        )
        self.layout.add_widget(self.result_label)

        
        self.fav_grid = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None
        )
        self.fav_grid.bind(minimum_height=self.fav_grid.setter('height'))

        scroll = ScrollView(
            size_hint=(0.9, 0.7),
            pos_hint={"center_x": 0.5, "y": 0.2}
        )
        scroll.add_widget(self.fav_grid)
        self.layout.add_widget(scroll)

        btn = MDRaisedButton(
            text="Yemek Ara",
            size_hint=(0.4, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05}
        )
        btn.bind(on_release=self.go_back)
        self.layout.add_widget(btn)

        self.add_widget(self.layout)

    def go_back(self, instance):
        self.manager.current = "first"

    def on_pre_enter(self):
      
        self.fav_grid.clear_widgets()
        cursor = connection.cursor()
        cursor.execute("SELECT Favorilerim FROM favtablo")
        for (favori,) in cursor.fetchall():
            btn = MDRaisedButton(
                text=f"⭐ {favori}",
                size_hint_y=None,
                height=50
            )
            btn.bind(on_release=lambda inst, y=favori: self.favori_detay(y))
            self.fav_grid.add_widget(btn)

    def favori_detay(self, yemek_ismi):
        #
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={yemek_ismi}"
        result = requests.get(url).json()

        if result["meals"]:
            detay = result["meals"][0]
            detay_ekran = DetayEkrani(detay, previous_screen="second", name="detay")

            if self.manager.has_screen("detay"):
                self.manager.remove_widget(self.manager.get_screen("detay"))

            self.manager.add_widget(detay_ekran)
            self.manager.current = "detay"
