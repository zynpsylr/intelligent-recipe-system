import requests
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from ekranlar.kategorisonuc import KategoriSonucEkrani  # kendi modülün

class İlkPencere(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    
        
        self.layout = FloatLayout()

    
        self.text_input = MDTextField(
            hint_text="Yemek ismini girin",
            size_hint=(0.8, None),
            height=50,
            pos_hint={"center_x": 0.5, "top": 0.95}
        )
        self.layout.add_widget(self.text_input)

       
        self.search_button = MDRaisedButton(
            text="Ara",
            size_hint=(0.3, None),
            height=50,
            pos_hint={"center_x": 0.5, "top": 0.88}
        )
        self.search_button.bind(on_press=self.arama_motoru)
        self.layout.add_widget(self.search_button)

      
        scroll = ScrollView(
            size_hint=(0.9, 0.4),
            pos_hint={"center_x": 0.5, "top": 0.82}
        )
        self.result_label = MDLabel(
            text="YEMEK TARİFİ YOK",
            size_hint_y=None,
            text_size=(Window.width*0.9, None),
            halign="left",
            valign="top"
        )
        self.result_label.bind(texture_size=self.result_label.setter("size"))
        scroll.add_widget(self.result_label)
        self.layout.add_widget(scroll)

      
        kategoriler = ["Beef", "Chicken", "Dessert", "Salad", "Pasta", "Seafood"]
        kategori_layout = GridLayout(
            cols=3,
            size_hint=(0.9, None),
            height=200,
            spacing=10,
            pos_hint={"center_x": 0.5, "top": 0.37}
        )
        for k in kategoriler:
            btn = MDRaisedButton(
                text=k,
                size_hint_y=None,
                height=60
            )
            btn.bind(on_press=lambda inst, cat=k: self.kategori_secildi(cat))
            kategori_layout.add_widget(btn)
        self.layout.add_widget(kategori_layout)

      
        btn_fav = MDRaisedButton(
            text="Favorilerim",
            size_hint=(0.4, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05}
        )
        btn_fav.bind(on_release=self.go_next)
        self.layout.add_widget(btn_fav)

        self.add_widget(self.layout)

    

    def arama_motoru(self, instance):
        yemek = self.text_input.text.strip()
        if yemek == "":
            self.result_label.text = " Lütfen yemek ismi giriniz."
            return

        my_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={yemek}"
        result = requests.get(my_url)
        data = result.json()

        if data["meals"]:
            filtered = [meal for meal in data["meals"] if meal["strMeal"].lower().startswith(yemek.lower())]
            metin = ""
            for idx, meal in enumerate(filtered, start=1):
                yemek_ismi = meal["strMeal"]
                kategori = meal["strCategory"]
                tarif = meal["strInstructions"]
                metin += f"🍽️ {idx}. İsim: {yemek_ismi}\n📂 Kategori: {kategori}\n📖 Tarif: {tarif}\n\n"
            self.result_label.text = metin if metin else "❌ Harfle başlayan yemek bulunamadı."
        else:
            self.result_label.text = "❌ Yemek bulunamadı."

    def kategori_secildi(self, kategori):
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={kategori}"
        result = requests.get(url)
        data = result.json()
        if data["meals"]:
            ekran_adi = f"kategori_{kategori}"
            ekran = KategoriSonucEkrani(kategori, data["meals"], name=ekran_adi)
            if self.manager.has_screen(ekran_adi):
                self.manager.remove_widget(self.manager.get_screen(ekran_adi))
            self.manager.add_widget(ekran)
            self.manager.current = ekran_adi
        else:
            self.result_label.text = f"❌ {kategori} kategorisinde yemek bulunamadı."

    def go_next(self, instance):
        self.manager.current = "second"
