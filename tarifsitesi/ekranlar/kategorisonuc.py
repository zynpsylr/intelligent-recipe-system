import requests
from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRaisedButton
from ekranlar.detayekrani import DetayEkrani

class KategoriSonucEkrani(MDScreen):
    def __init__(self, kategori, yemekler, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.title_label = MDRaisedButton(
            text=f"{kategori} Kategorisi",
            size_hint=(0.9, None),
            height=50,
            pos_hint={"center_x":0.5, "top":0.95}
        )
        self.layout.add_widget(self.title_label)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for meal in yemekler:
            btn = MDRaisedButton(text=meal["strMeal"], size_hint_y=None, height=50)
            btn.bind(on_release=lambda inst, m=meal: self.yemek_detay(m))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)

        back_btn = MDRaisedButton(text="⬅ Geri", size_hint_y=None, height=50)
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def yemek_detay(self, meal):
     
     meal_id = meal["idMeal"]

   
     url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
     result = requests.get(url).json()

     if result["meals"]:
        detay = result["meals"][0]  
        detay_ekran = DetayEkrani(detay, previous_screen=self.name, name="detay")

     
        if self.manager.has_screen("detay"):
            self.manager.remove_widget(self.manager.get_screen("detay"))

        self.manager.add_widget(detay_ekran)
        self.manager.current = "detay"

    def go_back(self, instance):
        self.manager.current = "first"
