#!/usr/bin/env python3
"""
ماشین حساب زیبا با PySide6
یک ماشین حساب مدرن با ظاهر شیشه‌ای (glassmorphism) و انیمیشن‌های ساده
"""

import sys
import re
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ماشین حساب")
        self.setFixedSize(380, 560)
        self.expression = ""
        self.just_evaluated = False
        self._build_ui()
        self._apply_styles()

    # ---------------------------------------------------------------- UI ---
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # ---- نمایشگر تاریخچه کوچک ----
        self.history_label = QLabel("")
        self.history_label.setObjectName("historyLabel")
        self.history_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addWidget(self.history_label)

        # ---- صفحه نمایش اصلی ----
        self.display = QLineEdit("0")
        self.display.setObjectName("display")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setReadOnly(True)
        self.display.setMinimumHeight(80)
        font = QFont("Segoe UI", 32, QFont.DemiBold)
        self.display.setFont(font)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 90))
        shadow.setOffset(0, 4)
        self.display.setGraphicsEffect(shadow)

        main_layout.addWidget(self.display)

        # ---- دکمه‌ها ----
        grid = QGridLayout()
        grid.setSpacing(12)

        buttons = [
            ("C", 0, 0, "func"), ("⌫", 0, 1, "func"), ("%", 0, 2, "func"), ("÷", 0, 3, "op"),
            ("7", 1, 0, "num"), ("8", 1, 1, "num"), ("9", 1, 2, "num"), ("×", 1, 3, "op"),
            ("4", 2, 0, "num"), ("5", 2, 1, "num"), ("6", 2, 2, "num"), ("−", 2, 3, "op"),
            ("1", 3, 0, "num"), ("2", 3, 1, "num"), ("3", 3, 2, "num"), ("+", 3, 3, "op"),
            ("±", 4, 0, "func"), ("0", 4, 1, "num"), (".", 4, 2, "num"), ("=", 4, 3, "equal"),
        ]

        for text, row, col, kind in buttons:
            btn = QPushButton(text)
            btn.setObjectName(kind)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumSize(QSize(70, 70))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFont(QFont("Segoe UI", 18, QFont.Medium))
            btn.clicked.connect(lambda checked=False, t=text: self.on_button(t))
            grid.addWidget(btn, row, col)

        main_layout.addLayout(grid)

    # ------------------------------------------------------------- STYLE ---
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1b4b, stop:0.5 #312e81, stop:1 #4c1d95
                );
                font-family: 'Segoe UI', sans-serif;
            }

            #historyLabel {
                color: rgba(255, 255, 255, 120);
                font-size: 14px;
                padding-right: 6px;
                min-height: 20px;
            }

            #display {
                background: rgba(255, 255, 255, 18);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 18px;
                color: #ffffff;
                padding: 0 20px;
            }

            QPushButton {
                border-radius: 20px;
                border: none;
                color: white;
            }

            QPushButton#num {
                background: rgba(255, 255, 255, 25);
            }
            QPushButton#num:hover {
                background: rgba(255, 255, 255, 45);
            }
            QPushButton#num:pressed {
                background: rgba(255, 255, 255, 65);
            }

            QPushButton#func {
                background: rgba(255, 255, 255, 15);
                color: #c4b5fd;
            }
            QPushButton#func:hover {
                background: rgba(255, 255, 255, 35);
            }
            QPushButton#func:pressed {
                background: rgba(255, 255, 255, 55);
            }

            QPushButton#op {
                background: rgba(167, 139, 250, 60);
                color: #ffffff;
            }
            QPushButton#op:hover {
                background: rgba(167, 139, 250, 100);
            }
            QPushButton#op:pressed {
                background: rgba(167, 139, 250, 150);
            }

            QPushButton#equal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ec4899, stop:1 #8b5cf6
                );
                color: white;
                font-weight: bold;
            }
            QPushButton#equal:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f472b6, stop:1 #a78bfa
                );
            }
            QPushButton#equal:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #db2777, stop:1 #7c3aed
                );
            }
        """)

    # ------------------------------------------------------------- LOGIC ---
    def on_button(self, text):
        if text == "C":
            self.expression = ""
            self.history_label.setText("")
            self.display.setText("0")
            self.just_evaluated = False
            return

        if text == "⌫":
            self.expression = self.expression[:-1]
            self.display.setText(self._pretty(self.expression) or "0")
            return

        if text == "±":
            self._toggle_sign()
            return

        if text == "=":
            self._evaluate()
            return

        # تبدیل نمادهای نمایشی به عملگرهای پایتون
        symbol_map = {"×": "*", "÷": "/", "−": "-", "%": "/100*"}
        value = symbol_map.get(text, text)

        if self.just_evaluated:
            # اگر بعد از "=" عدد جدید بزنیم، عبارت پاک می‌شود
            if text.isdigit() or text == ".":
                self.expression = ""
            self.just_evaluated = False

        self.expression += value
        self.display.setText(self._pretty(self.expression))

    def _toggle_sign(self):
        # پیدا کردن آخرین عدد در عبارت و معکوس کردن علامتش
        match = re.search(r"(-?\d+\.?\d*)$", self.expression)
        if not match:
            return
        num = match.group(1)
        start = match.start(1)
        if num.startswith("-"):
            new_num = num[1:]
        else:
            new_num = "-" + num
        self.expression = self.expression[:start] + new_num
        self.display.setText(self._pretty(self.expression))

    def _pretty(self, expr):
        """نمایش نمادهای زیبا به‌جای عملگرهای پایتون"""
        pretty = expr
        pretty = pretty.replace("*", "×")
        pretty = pretty.replace("/100*", "%")
        pretty = pretty.replace("/", "÷")
        pretty = pretty.replace("-", "−")
        return pretty

    def _evaluate(self):
        if not self.expression:
            return
        try:
            # فقط کاراکترهای مجاز اجازه محاسبه دارند
            if not re.fullmatch(r"[0-9+\-*/.%() ]+", self.expression):
                raise ValueError("invalid")
            result = eval(self.expression, {"__builtins__": {}}, {})
            self.history_label.setText(self._pretty(self.expression) + " =")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            result_str = str(round(result, 10)) if isinstance(result, float) else str(result)
            self.display.setText(result_str)
            self.expression = result_str
            self.just_evaluated = True
        except (ZeroDivisionError, SyntaxError, ValueError, TypeError, OverflowError):
            self.display.setText("خطا")
            self.expression = ""
            self.just_evaluated = True

    # -------------------------------------------------------- KEYBOARD ---
    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        key_map = {
            Qt.Key_Plus: "+", Qt.Key_Minus: "−",
            Qt.Key_Asterisk: "×", Qt.Key_Slash: "÷",
            Qt.Key_Enter: "=", Qt.Key_Return: "=",
            Qt.Key_Backspace: "⌫", Qt.Key_Delete: "C",
            Qt.Key_Percent: "%",
        }

        if key in key_map:
            self.on_button(key_map[key])
        elif text.isdigit() or text == ".":
            self.on_button(text)
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LeftToRight)  # صفحه‌کلید محاسباتی چپ‌به‌راست بهتر است
    window = Calculator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
