"""
Módulo principal da aplicação.
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def main():
    """Função principal da aplicação."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 