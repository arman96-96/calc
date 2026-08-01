# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget

Window.size = (400, 650)


class CalcButton(Button):
    pass


class Calculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""
        self.display_text = "0"

    def on_button_press(self, instance):
        text = instance.text

        if text == "C":
            self.expression = ""
            self.display_text = "0"
        elif text == "⌫":
            self.expression = self.expression[:-1]
            self.display_text = self.expression if self.expression else "0"
        elif text == "=":
            try:
                # تبدیل نمادها برای محاسبه
                expr = self.expression.replace("×", "*").replace("÷", "/")
                result = str(eval(expr))
                # حذف صفرهای اضافی اعشاری
                if "." in result:
                    result = result.rstrip("0").rstrip(".")
                self.display_text = result
                self.expression = result
            except Exception:
                self.display_text = "خطا"
                self.expression = ""
        elif text == "±":
            if self.expression and self.expression[0] == "-":
                self.expression = self.expression[1:]
            elif self.expression:
                self.expression = "-" + self.expression
            self.display_text = self.expression if self.expression else "0"
        elif text == "%":
            try:
                result = str(float(self.expression) / 100)
                self.expression = result
                self.display_text = result
            except Exception:
                pass
        else:
            if self.display_text == "0" and text not in [".", "+", "-", "×", "÷"]:
                self.expression = text
            else:
                self.expression += text
            self.display_text = self.expression

        self.ids.display.text = self.display_text


class CalculatorApp(App):
    def build(self):
        self.title = "ماشین حساب"
        return Calculator()


if __name__ == "__main__":
    CalculatorApp().run()