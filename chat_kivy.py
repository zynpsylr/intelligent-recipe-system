import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView 
from kivy.core.window import Window
from graph.rag_graph import RAGGraph


class ChatApp(App):
    def build(self):

        self.rag_graph = RAGGraph()
        self.is_setup = False
        def setup(self):
             
             """Chatbot kurulumu"""
             if self.is_setup:
                 print("✅ Setup zaten tamamlanmış!")
                 return
             
             print("🚀 RAG Chatbot kurulumu başlıyor...")
             
             # Veri kurulumu
             self.rag_graph.setup_data()
             
             # Graph oluştur
             self.rag_graph.create_graph()
             
             self.is_setup = True
             print("✅ Setup tamamlandı!")

        setup(self)
        # Pencere arkaplan rengini ayarlar
        Window.clearcolor = (0.2, 0.2, 0.2, 1)
        
        # Tüm UI öğelerini tutacak ana dikey BoxLayout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.chat_scroll_view = ScrollView()

        # Kaydırılabilir alanın içine mesajları yerleştirmek için dikey bir BoxLayout
        self.chat_history = BoxLayout(
            orientation='vertical',
            size_hint_y=None,  # Yüksekliğin sabit değil, içeriğe göre ayarlanmasını sağlar
            spacing=10
        )
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        self.chat_scroll_view.add_widget(self.chat_history)
        self.main_layout.add_widget(self.chat_scroll_view)

      # soru inputu kısmı sabit 
        self.input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )

        self.question_input = TextInput(
            hint_text="Sorunuzu giriniz...",
            size_hint_y=None,
            size_hint_x=1,
            height=50,
            font_size=18,
            multiline=False  # Tek satır giriş için False
        )

        self.send_button = Button(
            text="Gönder",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=120,
            font_size=20,
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
        )

        # "Gönder" butonuna basma olayını bağlar
        self.send_button.bind(on_press=self.on_send_button_press)

        # Giriş bileşenlerini yatay düzene ekler
        self.input_layout.add_widget(self.question_input)
        self.input_layout.add_widget(self.send_button)
        self.main_layout.add_widget(self.input_layout)

        return self.main_layout
   

    def on_send_button_press(self, instance):
        user_message = self.question_input.text.strip()
        if user_message:
            # Kullanıcı mesajını ekrana ekler
            self.add_message(user_message, "user")
            # Giriş kutusunu temizler
            self.question_input.text = ""
            # Rag chatbota ask fonsksiyonu ile soru gönderilir
            self.response=self.rag_graph.ask (user_message)
             # Bot yanıtını ekrana ekler
            self.add_message(self.response, "bot")
          

    def add_message(self, text, sender):
        """Mesajları sohbet geçmişine ekler ve stillendirir."""
        message_label = Label(
            text=text,
            halign='right' if sender == 'user' else 'left', # Kullanıcı mesajı sağa, bot mesajı sola hizalı
            valign='top',
            text_size=(self.chat_history.width - 20, None), # Label'in genişliğini ayarlar
            font_size=18,
            color=(1, 1, 1, 1) if sender == 'user' else (0.8, 0.8, 0.8, 1), # Mesaj rengini ayarlar
            size_hint=(1, None),
            padding=(10, 10),
        )
        message_label.bind(texture_size=message_label.setter('size'))

        # Mesajı sohbet geçmişine ekler
        self.chat_history.add_widget(message_label)



if __name__ == '__main__':
    ChatApp().run()
