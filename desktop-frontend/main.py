# desktop-frontend/main.py
import sys
import requests

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QInputDialog,
    QLineEdit,
    QGroupBox,
    QTabWidget,
    QHeaderView,
)
from PyQt5.QtCore import Qt

import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt  # noqa: E402

API_BASE = "http://127.0.0.1:8000/api"


class App(QWidget):
    def __init__(self):
        super().__init__()

        # --- global style (roughly matching your web theme) ---
        self.setStyleSheet(
            """
            QWidget {
                background-color: #020617;
                color: #e5e7eb;
                font-family: Segoe UI, system-ui, sans-serif;
                font-size: 12px;
            }
            QLabel#TitleLabel {
                font-size: 18px;
                font-weight: 600;
            }
            QLabel#SubtitleLabel {
                color: #9ca3af;
                font-size: 11px;
            }
            QPushButton {
                border-radius: 18px;
                padding: 6px 16px;
                color: #020617;
                background-color: #FFF58A; /* soft yellow */
                border: none;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #ffe769;
            }
            QPushButton:pressed {
                background-color: #e6d259;
            }
            QPushButton#GhostButton {
                background-color: transparent;
                color: #e5e7eb;
                border: 1px solid #4b5563;
            }
            QPushButton#GhostButton:hover {
                background-color: #111827;
            }
            QGroupBox {
                border: 1px solid #111827;
                border-radius: 14px;
                margin-top: 10px;
                padding: 10px 12px 12px 12px;
                background-color: #020617;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: #9ca3af;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.12em;
            }
            QTabWidget::pane {
                border-top: 1px solid #111827;
                margin-top: 6px;
            }
            QTabBar::tab {
                background: transparent;
                color: #9ca3af;
                border: none;
                padding: 6px 14px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                color: #e5e7eb;
                border-bottom: 2px solid #FFBBE1; /* pink accent */
            }
            QTableWidget {
                gridline-color: #1f2933;
                selection-background-color: #1d4ed8;
                selection-color: white;
                background-color: #020617;
                alternate-background-color: #020b29;
            }
            QHeaderView::section {
                background-color: #020b29;
                color: #9ca3af;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #1f2933;
            }
            """
        )

        self.setWindowTitle("Chemical Equipment Parameter Visualizer (Desktop)")
        self.resize(960, 620)

        # --- auth state ---
        self.auth_token = None
        self.auth_user = None

        # === ROOT LAYOUT ===
        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        self.setLayout(root)

        # === HEADER / NAVBAR ===
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        self.title_label = QLabel("Chemical Equipment Parameter Visualizer")
        self.title_label.setObjectName("TitleLabel")
        self.subtitle_label = QLabel(f"API: {API_BASE}")
        self.subtitle_label.setObjectName("SubtitleLabel")

        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)

        header.addLayout(title_box)
        header.addStretch()

        # right side: "Logged in as" + login/logout button
        self.user_label = QLabel("Logged out")
        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("GhostButton")
        self.login_btn.clicked.connect(self.handle_auth_button)

        header.addWidget(self.user_label)
        header.addSpacing(8)
        header.addWidget(self.login_btn)

        root.addLayout(header)

        # === TABS ===
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # ---------- OVERVIEW TAB ----------
        overview = QWidget()
        ov_layout = QVBoxLayout()
        ov_layout.setSpacing(10)
        overview.setLayout(ov_layout)

        # top buttons row for overview
        btn_row = QHBoxLayout()
        self.btn_upload = QPushButton("Upload CSV")
        self.btn_refresh = QPushButton("Refresh Latest Summary")
        self.btn_pdf = QPushButton("Download Latest PDF")

        btn_row.addWidget(self.btn_upload)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addWidget(self.btn_pdf)
        btn_row.addStretch()
        ov_layout.addLayout(btn_row)

        # summary group
        self.summary_group = QGroupBox("Dataset Summary")
        sg_layout = QVBoxLayout()
        self.summary_label = QLabel("No summary loaded yet. Upload a CSV or refresh latest.")
        self.summary_label.setWordWrap(True)
        sg_layout.addWidget(self.summary_label)

        tip = QLabel(
            "Tip: After loading a dataset, a bar chart for Equipment Type Distribution will pop up."
        )
        tip.setStyleSheet("color: #9ca3af; font-size: 11px;")
        sg_layout.addWidget(tip)

        self.summary_group.setLayout(sg_layout)
        ov_layout.addWidget(self.summary_group)

        self.tabs.addTab(overview, "Overview")

        # ---------- HISTORY TAB ----------
        history_tab = QWidget()
        h_layout = QVBoxLayout()
        h_layout.setSpacing(10)
        history_tab.setLayout(h_layout)

        h_btn_row = QHBoxLayout()
        self.btn_history = QPushButton("Load Last 5 Uploads")
        h_btn_row.addWidget(self.btn_history)
        h_btn_row.addStretch()
        h_layout.addLayout(h_btn_row)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Filename", "Uploaded At", "Total Rows"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        history_group = QGroupBox("Last 5 Uploads")
        hg_layout = QVBoxLayout()
        hg_layout.addWidget(self.table)
        history_group.setLayout(hg_layout)
        h_layout.addWidget(history_group)

        self.tabs.addTab(history_tab, "Upload History")

        # === SIGNALS ===
        self.btn_upload.clicked.connect(self.upload_csv)
        self.btn_refresh.clicked.connect(self.load_latest)
        self.btn_history.clicked.connect(self.load_history)
        self.btn_pdf.clicked.connect(self.download_pdf)

    # ======================== HELPERS ========================

    def alert(self, title, message):
        QMessageBox.information(self, title, message)

    def _auth_headers(self):
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Token {self.auth_token}"
        return headers

    def _ensure_logged_in(self):
        """Return True if logged in, otherwise show a message and return False."""
        if not self.auth_token:
            self.alert("Login required", "Please log in first to use this feature.")
            return False
        return True

    # ======================== AUTH ========================

    def handle_auth_button(self):
        """Login if logged out; logout if logged in."""
        if self.auth_token:
            # logout
            try:
                requests.post(f"{API_BASE}/auth/logout/", headers=self._auth_headers())
            except Exception:
                pass  # ignore errors

            self.auth_token = None
            self.auth_user = None
            self.user_label.setText("Logged out")
            self.login_btn.setText("Login")
            self.alert("Logged out", "You have been logged out.")
            return

        # otherwise login
        username, ok = QInputDialog.getText(self, "Login", "Username:")
        if not ok or not username:
            return

        password, ok = QInputDialog.getText(
            self, "Login", "Password:", QLineEdit.Password
        )
        if not ok or not password:
            return

        try:
            resp = requests.post(
                f"{API_BASE}/auth/login/",
                json={"username": username, "password": password},
            )
            resp.raise_for_status()
            data = resp.json()
            self.auth_token = data.get("token")
            self.auth_user = data.get("username")
            self.user_label.setText(f"Logged in as <b>{self.auth_user}</b>")
            self.login_btn.setText("Log out")
            self.alert("Login", f"Logged in as {self.auth_user}")
        except Exception as e:
            self.alert("Error", f"Login failed: {e}")

    # ======================== API CALLS ========================

    def upload_csv(self):
        if not self._ensure_logged_in():
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Choose CSV", filter="CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "rb") as f:
                resp = requests.post(
                    f"{API_BASE}/upload/", files={"file": f}, headers=self._auth_headers()
                )

            if resp.status_code >= 400:
                raise RuntimeError(resp.text)

            data = resp.json()
            self.render_summary(data)
            self.alert("Upload Successful", f"Uploaded: {data.get('filename')}")
        except Exception as e:
            self.alert("Error", str(e))

    def load_latest(self):
        if not self._ensure_logged_in():
            return

        try:
            resp = requests.get(
                f"{API_BASE}/summary/latest/", headers=self._auth_headers()
            )
            if resp.status_code == 404:
                self.summary_label.setText(
                    "No datasets yet. Upload a CSV first."
                )
                return
            resp.raise_for_status()
            self.render_summary(resp.json())
        except Exception as e:
            self.alert("Error", str(e))

    def load_history(self):
        if not self._ensure_logged_in():
            return

        try:
            resp = requests.get(f"{API_BASE}/history/", headers=self._auth_headers())
            resp.raise_for_status()
            items = resp.json().get("items", [])

            self.table.setRowCount(0)
            for it in items:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(it.get("filename")))
                self.table.setItem(row, 1, QTableWidgetItem(str(it.get("uploaded_at"))))
                self.table.setItem(
                    row, 2, QTableWidgetItem(str(it["summary"]["total_count"]))
                )
        except Exception as e:
            self.alert("Error", str(e))

    def download_pdf(self):
        if not self._ensure_logged_in():
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report As",
            "latest_equipment_report.pdf",
            "PDF Files (*.pdf)",
        )
        if not save_path:
            return

        try:
            resp = requests.get(
                f"{API_BASE}/report/latest/",
                stream=True,
                headers=self._auth_headers(),
            )
            resp.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            self.alert("Report Saved", f"Saved to: {save_path}")
        except Exception as e:
            self.alert("Error", str(e))

    # ======================== UI HELPERS ========================

    def render_summary(self, data):
        av = data.get("averages", {})
        text = (
            f"<b>Latest Dataset</b><br>"
            f"File: {data.get('filename')}<br>"
            f"Total Rows: {data.get('total_count')}<br>"
            f"Avg Flowrate: {av.get('Flowrate')} | "
            f"Avg Pressure: {av.get('Pressure')} | "
            f"Avg Temperature: {av.get('Temperature')}"
        )
        self.summary_label.setText(text)

        # show bar chart
        dist = data.get("type_distribution", {})
        if dist:
            labels = list(dist.keys())
            values = list(dist.values())
            plt.figure()
            plt.bar(labels, values, color=["#FFF58A", "#FFBBE1", "#DD7BDF", "#B3BFFF"])
            plt.title("Equipment Type Distribution")
            plt.xlabel("Type")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
