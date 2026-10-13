"""Main window. Thin — all logic lives in the engine."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

from aive.core.engine import EditorEngine


class MainWindow(QMainWindow):
    def __init__(self, engine: EditorEngine) -> None:
        super().__init__()
        self._engine = engine
        self.setWindowTitle("AI Video Editor Toolkit")
        self.resize(1280, 800)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Timeline, preview, and AI tools load here."))
        self.setCentralWidget(central)
        engine.on_timeline_change(self._on_timeline)


    def _on_timeline(self, timeline) -> None:
        self.statusBar().showMessage(
            f"{len(timeline.clips)} clips · {timeline.total_duration():.1f}s"
        )


def launch_ui(engine: EditorEngine) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    win = MainWindow(engine)
    win.show()
    return app.exec()