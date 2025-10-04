
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from baglanti import connection

class DetayEkrani(MDScreen):
    def __init__(self, meal, previous_screen, **kwargs):
        super().__init__(**kwargs)
        self.meal = meal
        self.previous_screen = previous_screen  
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

       
        image = AsyncImage(source=meal["strMealThumb"], size=(200, 200), size_hint=(None,None),pos_hint={'center_x':0.5})
        layout.add_widget(image)

     
        label = MDLabel(
            text=f"🍽️ {meal['strMeal']}\n📂 Kategori: {meal.get('strCategory','?')}",
            halign="center"
        )
        layout.add_widget(label)

   
        tarif = meal.get("strInstructions", "Tarif bulunamadı")
        scroll = ScrollView(size_hint=(1, 1))
        tarif_label = MDLabel(text=tarif, halign="left", valign="top", size_hint_y=None)
        tarif_label.bind(texture_size=tarif_label.setter("size"))
        scroll.add_widget(tarif_label)
        layout.add_widget(scroll)
           
       
        btn_favori = MDRaisedButton(text="Favorilere Ekle")
        btn_favori.bind(on_release=self.favorilere_ekle)
        layout.add_widget(btn_favori)

       
        back_btn = MDRaisedButton(text="⬅ Geri", size_hint_y=None, height=50)
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)

      
        btn = MDRaisedButton(text="Yemek Ara",size_hint_y=None, height=50)
        btn.bind(on_release=self.go_back)
        layout.add_widget(btn)


        

        self.add_widget(layout)

    def favorilere_ekle(self, instance):
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO favtablo(Favorilerim) VALUES(?)", (self.meal["strMeal"],))
            connection.commit()
            print(f"✅ {self.meal['strMeal']} favorilere eklendi.")
        except Exception as e:
            print("⚠ Hata:", e)

    def go_back(self, instance):
         self.manager.current = self.previous_screen