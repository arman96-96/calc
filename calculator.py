import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QGridLayout, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush


class CalcButton(QPushButton):
    """دکمه‌ی سفارشی با افکت hover و press"""
    def __init__(self, text, color="#3a3a4a", text_color="white", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.text_color = text_color
        self.setFixedHeight(70)
        self.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: {self.text_color};
                border: none;
                border-radius: 18px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten(self.color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken(self.color, 20)};
            }}
        """)

    @staticmethod
    def _lighten(hex_color, percent):
        num = int(hex_color.lstrip('#'), 16)
        r = min(255, (num >> 16) + percent)
        g = min(255, ((num >> 8) & 0x00FF) + percent)
        b = min(255, (num & 0x0000FF) + percent)
        return f"#{(r << 16) | (g << 8) | b:06x}"

    @staticmethod
    def _darken(hex_color, percent):
        num = int(hex_color.lstrip('#'), 16)
        r = max(0, (num >> 16) - percent)
        g = max(0, ((num >> 8) & 0x00FF) - percent)
        b = max(0, (num & 0x0000FF) - percent)
        return f"#{(r << 16) | (g << 8) | b:06x}"


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ماشین حساب")
        self.setFixedSize(380, 600)
        self.expression = ""
        self.current_input = "0"
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # پس‌زمینه گرادیانت
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e2e, stop:1 #2d2d44);
            }
        """)

        # ===== نمایشگر =====
        display_frame = QFrame()
        display_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                padding: 15px;
            }
        """)
        display_layout = QVBoxLayout(display_frame)
        display_layout.setSpacing(5)

        self.history_label = QLabel("")
        self.history_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.history_label.setFont(QFont("Segoe UI", 14))
        self.history_label.setStyleSheet("color: #888; background: transparent;")

        self.display_label = QLabel("0")
        self.display_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.display_label.setStyleSheet("color: white; background: transparent;")

        display_layout.addWidget(self.history_label)
        display_layout.addWidget(self.display_label)
        main_layout.addWidget(display_frame)

        # ===== دکمه‌ها =====
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(12)

        buttons = [
            ('C',  '#ff6b6b', 'white'),   ('±',  '#4a4a5e', 'white'),
            ('%',  '#4a4a5e', 'white'),   ('÷',  '#ff9f43', 'white'),
            ('7',  '#3a3a4a', 'white'),   ('8',  '#3a3a4a', 'white'),
            ('9',  '#3a3a4a', 'white'),   ('×',  '#ff9f43', 'white'),
            ('4',  '#3a3a4a', 'white'),   ('5',  '#3a3a4a', 'white'),
            ('6',  '#3a3a4a', 'white'),   ('−',  '#ff9f43', 'white'),
            ('1',  '#3a3a4a', 'white'),   ('2',  '#3a3a4a', 'white'),
            ('3',  '#3a3a4a', 'white'),   ('+',  '#ff9f43', 'white'),
            ('⌫',  '#4a4a5e', 'white'),   ('0',  '#3a3a4a', 'white'),
            ('.',  '#3a3a4a', 'white'),   ('=',  '#4ecdc4', 'white'),
        ]

        positions = [(i // 4, i % 4) for i in range(len(buttons))]

        for (text, color, text_color), (row, col) in zip(buttons, positions):
            btn = CalcButton(text, color, text_color)
            btn.clicked.connect(lambda checked, t=text: self._on_click(t))
            buttons_layout.addWidget(btn, row, col)

        main_layout.addLayout(buttons_layout)

    def _on_click(self, text):
        if text == 'C':
            self.expression = ""
            self.current_input = "0"
            self.display_label.setText("0")
            self.history_label.setText("")
        elif text == '⌫':
            self.current_input = self.current_input[:-1] or "0"
            self.display_label.setText(self.current_input)
        elif text == '±':
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            elif self.current_input != '0':
                self.current_input = '-' + self.current_input
            self.display_label.setText(self.current_input)
        elif text == '%':
            try:
                val = float(self.current_input) / 100
                self.current_input = str(val)
                self.display_label.setText(self.current_input)
            except:
                pass
        elif text in ('+', '−', '×', '÷'):
            op_map = {'+': '+', '−': '-', '×': '*', '÷': '/'}
            self.expression += self.current_input + op_map[text]
            self.history_label.setText(self.expression)
            self.current_input = "0"
        elif text == '=':
            self.expression += self.current_input
            self.history_label.setText(self.expression + " =")
            try:
                result = eval(self.expression)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.current_input = str(result)
                self.display_label.setText(self.current_input)
            except:
                self.current_input = "خطا"
                self.display_label.setText("خطا")
            self.expression = ""
        else:  # اعداد و نقطه
            if text == '.' and '.' in self.current_input:
                return
            if self.current_input == '0' or self.current_input == 'خطا':
                self.current_input = text
            else:
                self.current_input += text
            self.display_label.setText(self.current_input)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Calculator()
    window.show()
    sys.exit(app.exec())