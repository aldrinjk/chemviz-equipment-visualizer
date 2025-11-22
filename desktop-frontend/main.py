import sys
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QInputDialog,
    QLineEdit,
    QGroupBox,
)
from PyQt5.QtCore import Qt
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

API_BASE = "http://127.0.0.1:8000/api"


class App(QWidget):
    def __init__(self):
        super().__init__()

        # ---- Global style ----
        self.setStyleSheet(
            """
        QWidget {
            background-color: #020617;
            color: #e5e7eb;
            font-family: Segoe UI, system-ui, sans-serif;
            font-size: 12px;
        }
        QGroupBox {
            border: 1px solid #1f2933;
            border-radius: 10px;
            margin-top: 16px;
            padding: 12px;
            background-color: #050816;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
            color: #9ca3af;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }
        QPushButton {
            border-radius: 18px;
            padding: 6px 14px;
            color: white;
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563eb,
                stop:1 #38bdf8
            );
        }
        QPushButton:hover {
            background-color: #3b82f6;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
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
        self.resize(900, 600)

        # ---- Main layout ----
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Header label
        title = QLabel("Chemical Equipment Parameter Visualizer (Desktop)")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 600; margin-bottom: 4px;"
        )
        subtitle = QLabel(f"API: {API_BASE}")
        subtitle.setStyleSheet(
            "color: #9ca3af; font-size: 11px; margin-bottom: 8px;"
        )

        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)

        # Store auth token
        self.auth_token = None

        # ---- Controls / buttons ----
        self.btn_upload = QPushButton("Upload CSV")
        self.btn_latest = QPushButton("Refresh Latest Summary")
        self.btn_history = QPushButton("Load History (Last 5)")
        self.btn_pdf = QPushButton("Download Latest PDF")
        self.btn_login = QPushButton("Login")

        # ---- Summary label ----
        self.summary_label = QLabel("No summary loaded.")
        self.summary_label.setWordWrap(True)

        # ---- History table ----
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Filename", "Uploaded At", "Total Rows"]
        )

        # ---- Group: Upload & Controls ----
        upload_group = QGroupBox("Upload & Controls")
        upload_layout = QHBoxLayout()
        upload_group.setLayout(upload_layout)

        upload_layout.addWidget(self.btn_upload)
        upload_layout.addWidget(self.btn_latest)
        upload_layout.addWidget(self.btn_history)
        upload_layout.addWidget(self.btn_pdf)
        upload_layout.addStretch()
        upload_layout.addWidget(self.btn_login)

        self.layout.addWidget(upload_group)

        # ---- Group: Latest Dataset ----
        summary_group = QGroupBox("Latest Dataset")
        summary_layout = QVBoxLayout()
        summary_group.setLayout(summary_layout)
        summary_layout.addWidget(self.summary_label)

        self.layout.addWidget(summary_group)

        # ---- Group: Upload History ----
        history_group = QGroupBox("Upload History (Last 5)")
        history_layout = QVBoxLayout()
        history_group.setLayout(history_layout)
        history_layout.addWidget(self.table)

        self.layout.addWidget(history_group)

        # Optional: keep info label if you want (not added to layout)
        self.info = QLabel(f"API: {API_BASE}")
        self.info.setStyleSheet("color: gray;")

        # ---- Hook up actions ----
        self.btn_upload.clicked.connect(self.upload_csv)
        self.btn_latest.clicked.connect(self.load_latest)
        self.btn_history.clicked.connect(self.load_history)
        self.btn_pdf.clicked.connect(self.download_pdf)
        self.btn_login.clicked.connect(self.login_user)

    # ----------------- Helpers -----------------

    def alert(self, title, message):
        QMessageBox.information(self, title, message)

    # ---------- Auth ----------

    def login_user(self):
        # Ask for username
        username, ok = QInputDialog.getText(self, "Login", "Username:")
        if not ok or not username:
            return

        # Ask for password (masked)
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
            if resp.status_code >= 400:
                raise RuntimeError(resp.text)
            data = resp.json()
            self.auth_token = data.get("token")
            self.alert("Login", f"Logged in as {data.get('username')}")
        except Exception as e:
            self.alert("Error", str(e))

    def _auth_headers(self):
        """Helper to add Authorization header if logged in."""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Token {self.auth_token}"
        return headers

    # ---------- API Calls ----------

    def upload_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose CSV", filter="CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            headers = self._auth_headers()
            with open(path, "rb") as f:
                resp = requests.post(
                    f"{API_BASE}/upload/", files={"file": f}, headers=headers
                )

            if resp.status_code >= 400:
                raise RuntimeError(resp.text)

            data = resp.json()
            self.render_summary(data)
            self.alert("Upload Successful", f"Uploaded: {data.get('filename')}")
        except Exception as e:
            self.alert("Error", str(e))

    def load_latest(self):
        # summary/latest is public
        try:
            resp = requests.get(f"{API_BASE}/summary/latest/")
            if resp.status_code == 404:
                self.summary_label.setText("No datasets yet. Upload a CSV first.")
                return
            resp.raise_for_status()
            self.render_summary(resp.json())
        except Exception as e:
            self.alert("Error", str(e))

    def load_history(self):
        # history is public too
        try:
            resp = requests.get(f"{API_BASE}/history/")
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
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report As",
            "latest_equipment_report.pdf",
            "PDF Files (*.pdf)",
        )
        if not save_path:
            return

        try:
            headers = self._auth_headers()
            resp = requests.get(
                f"{API_BASE}/report/latest/", stream=True, headers=headers
            )
            resp.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            self.alert("Report Saved", f"Saved to: {save_path}")
        except Exception as e:
            self.alert("Error", str(e))

    # ---------- UI Helpers ----------

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

        # Plot distribution
        dist = data.get("type_distribution", {})
        if dist:
            labels = list(dist.keys())
            values = list(dist.values())
            plt.figure()
            plt.bar(labels, values)
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
