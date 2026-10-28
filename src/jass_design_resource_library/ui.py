import os, sys, webbrowser
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from .models import Resource
from .services import CatalogService

def appdata():
    root=Path(os.environ.get("LOCALAPPDATA",Path.home()/".local/share"))
    return root/"JASS"/"DesignResourceLibrary"/"resources.sqlite3"

class ResourceDialog(QDialog):
    def __init__(self,parent=None,r=None):
        super().__init__(parent); self.r=r; self.setWindowTitle("Resource details"); self.resize(480,520)
        self.name=QLineEdit(r.name if r else "")
        self.category=QComboBox(); self.category.addItems(["Accessibility","Backgrounds","Colour Tools","Design Systems","Design Tools","Desktop Software","Fonts","Icons","Illustrations","Inspiration","React UI","Templates","UI Components","UX Learning","Other"])
        self.description=QTextEdit(); self.description.setPlainText(r.description if r else ""); self.description.setMaximumHeight(65)
        self.url=QLineEdit(r.url if r else "")
        self.platform=QComboBox(); self.platform.addItems(["Web","React","Windows/Linux/macOS","Windows","Linux","macOS","Cross-platform","Other"])
        self.pricing=QComboBox(); self.pricing.addItems(["Free","Free + paid","Paid","Unknown"])
        self.licence=QLineEdit(r.licence if r else "Check provider")
        self.status=QComboBox(); self.status.addItems(["Not checked","Working","Broken","Terms reviewed"])
        self.tags=QLineEdit(r.tags if r else ""); self.favorite=QCheckBox("Favourite"); self.favorite.setChecked(r.favorite if r else False)
        self.notes=QTextEdit(); self.notes.setPlainText(r.notes if r else ""); self.notes.setMaximumHeight(65)
        if r:
            for w,val in [(self.category,r.category),(self.platform,r.platform),(self.pricing,r.pricing),(self.status,r.status)]: w.setCurrentText(val)
        form=QFormLayout(self)
        for label,w in [("Name *",self.name),("Category",self.category),("Description",self.description),("URL *",self.url),("Platform",self.platform),("Pricing",self.pricing),("Licence reminder",self.licence),("Review status",self.status),("Tags",self.tags),("",self.favorite),("Notes",self.notes)]: form.addRow(label,w)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)
    def value(self):
        return Resource(id=self.r.id if self.r else None,name=self.name.text(),category=self.category.currentText(),description=self.description.toPlainText(),url=self.url.text(),platform=self.platform.currentText(),pricing=self.pricing.currentText(),licence=self.licence.text(),status=self.status.currentText(),tags=self.tags.text(),favorite=self.favorite.isChecked(),notes=self.notes.toPlainText())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.s=CatalogService(appdata()); self.setWindowTitle("JASS Design Resource Library v0.1.0"); self.resize(1150,700)
        root=QWidget(); v=QVBoxLayout(root)
        title=QLabel("JASS Design Resource Library"); title.setStyleSheet("font-size:22px;font-weight:bold")
        v.addWidget(title); v.addWidget(QLabel("Search and organize design assets, UI libraries, templates, and inspiration."))
        row=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Search name, description, URL, tags, notes…")
        self.category=QComboBox(); self.platform=QComboBox(); self.platform.addItems(["All","Web","React","Windows/Linux/macOS","Windows","Linux","macOS","Cross-platform","Other"])
        self.pricing=QComboBox(); self.pricing.addItems(["All","Free","Free + paid","Paid","Unknown"])
        self.status=QComboBox(); self.status.addItems(["All","Not checked","Working","Broken","Terms reviewed"]); self.favs=QCheckBox("Favourites only")
        for label,w in [("Search",self.search),("Category",self.category),("Platform",self.platform),("Pricing",self.pricing),("Status",self.status)]: row.addWidget(QLabel(label)); row.addWidget(w,2 if w is self.search else 1)
        row.addWidget(self.favs); v.addLayout(row)
        buttons=QHBoxLayout()
        for label,fn in [("Add",self.add),("Edit",self.edit),("Delete",self.delete),("Toggle favourite",self.toggle),("Open website",self.open_url),("Export CSV",self.export)]:
            b=QPushButton(label); b.clicked.connect(fn); buttons.addWidget(b)
        v.addLayout(buttons)
        self.table=QTableWidget(0,7); self.table.setHorizontalHeaderLabels(["★","Name","Category","Platform","Pricing","Status","URL"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows); self.table.setSelectionMode(QAbstractItemView.SingleSelection); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch); self.table.horizontalHeader().setSectionResizeMode(6,QHeaderView.Stretch)
        v.addWidget(self.table,1); self.footer=QLabel(); v.addWidget(self.footer); self.setCentralWidget(root)
        self.search.textChanged.connect(self.refresh)
        for w in [self.category,self.platform,self.pricing,self.status]: w.currentTextChanged.connect(self.refresh)
        self.favs.toggled.connect(self.refresh); self.table.doubleClicked.connect(self.open_url); self.refresh()
    def selected(self):
        row=self.table.currentRow()
        return self.s.get(self.table.item(row,0).data(Qt.UserRole)) if row>=0 else None
    def refresh(self,*_):
        old=self.category.currentText(); self.category.blockSignals(True); self.category.clear(); self.category.addItems(["All"]+self.s.categories()); self.category.setCurrentText(old if old in ["All"]+self.s.categories() else "All"); self.category.blockSignals(False)
        rows=self.s.list(self.search.text(),self.category.currentText(),self.platform.currentText(),self.pricing.currentText(),self.status.currentText(),self.favs.isChecked())
        self.table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,val in enumerate(["★" if r.favorite else "☆",r.name,r.category,r.platform,r.pricing,r.status,r.url]):
                item=QTableWidgetItem(str(val))
                if j==0: item.setData(Qt.UserRole,r.id); item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i,j,item)
        self.footer.setText(f"{len(rows)} resources shown · Stored locally · Verify licences and availability before use")
    def add(self):
        d=ResourceDialog(self)
        if d.exec()==QDialog.Accepted:
            try:self.s.save(d.value()); self.refresh()
            except ValueError as e:QMessageBox.warning(self,"Invalid entry",str(e))
    def edit(self):
        r=self.selected()
        if not r:return QMessageBox.information(self,"Select resource","Select a resource first.")
        d=ResourceDialog(self,r)
        if d.exec()==QDialog.Accepted:
            try:self.s.save(d.value()); self.refresh()
            except ValueError as e:QMessageBox.warning(self,"Invalid entry",str(e))
    def delete(self):
        r=self.selected()
        if r and QMessageBox.question(self,"Delete",f"Remove '{r.name}' from your catalogue?")==QMessageBox.Yes:self.s.delete(r.id); self.refresh()
    def toggle(self):
        r=self.selected()
        if r:self.s.toggle(r.id); self.refresh()
    def open_url(self):
        r=self.selected()
        if r:webbrowser.open(r.url)
    def export(self):
        path,_=QFileDialog.getSaveFileName(self,"Export catalogue","jass-design-resources.csv","CSV files (*.csv)")
        if path:
            try:QMessageBox.information(self,"Export complete",f"Exported {self.s.export(path)} resources.")
            except OSError as e:QMessageBox.critical(self,"Export failed",str(e))

def main():
    app=QApplication(sys.argv); app.setStyle("Fusion"); w=MainWindow(); w.show(); return app.exec()
