import csv, sqlite3
from pathlib import Path
from urllib.parse import urlparse
from .models import Resource

SEED = [
("Google Fonts","Fonts","Font families and typography.","https://fonts.google.com/","Web","Free","Check individual font licence","typography,fonts"),
("Lucide","Icons","Open-source SVG icon library.","https://lucide.dev/icons/","Web","Free","Check current licence","icons,svg,ui"),
("Heroicons","Icons","Hand-crafted SVG icons.","https://heroicons.com/","Web","Free","Check current licence","icons,svg"),
("Tabler Icons","Icons","Collection of SVG icons.","https://tabler.io/icons","Web","Free","Check current licence","icons,svg"),
("Flowbite","UI Components","UI components and templates.","https://flowbite.com/","Web","Free + paid","Check package and asset licences","ui,tailwind"),
("daisyUI","UI Components","Tailwind CSS component library.","https://daisyui.com/","Web","Free","Check current licence","ui,tailwind"),
("Mantine","React UI","React components and hooks.","https://mantine.dev/","React","Free","Check current licence","react,components"),
("Material UI","React UI","React components based on Material Design.","https://mui.com/","React","Free + paid","Check package licences","react,material"),
("HTML5 UP","Templates","Responsive website templates.","https://html5up.net/","Web","Free","Review attribution and usage terms","templates,html,css"),
("Start Bootstrap","Templates","Bootstrap themes and templates.","https://startbootstrap.com/","Web","Free + paid","Check each template licence","bootstrap,templates"),
("unDraw","Illustrations","Customizable illustrations.","https://undraw.co/illustrations","Web","Free","Check current terms","illustrations,svg"),
("Haikei","Backgrounds","Generate SVG backgrounds and patterns.","https://haikei.app/","Web","Free + paid","Check current plan terms","svg,backgrounds"),
("Penpot","Design Tools","Open-source design and prototyping platform.","https://penpot.app/","Web","Free","Check current terms","design,prototype"),
("Figma","Design Tools","Collaborative interface design.","https://www.figma.com/","Web","Free + paid","Check plan and asset licences","design,prototype"),
("GIMP","Desktop Software","Free, open-source image editor.","https://www.gimp.org/","Windows/Linux/macOS","Free","Software licence differs from asset licences","image,editor"),
("Inkscape","Desktop Software","Open-source vector graphics editor.","https://inkscape.org/","Windows/Linux/macOS","Free","Software licence differs from asset licences","svg,vector"),
("Krita","Desktop Software","Open-source painting application.","https://krita.org/","Windows/Linux/macOS","Free","Software licence differs from asset licences","painting,graphics"),
("Land-book","Inspiration","Website design inspiration gallery.","https://land-book.com/","Web","Free + paid","Reference only; check asset rights","inspiration,websites"),
("Dribbble","Inspiration","Design portfolio and inspiration community.","https://dribbble.com/","Web","Free + paid","Do not reuse work without permission","inspiration,ui"),
("Checklist Design","Design Systems","Checklists for pages and components.","https://www.checklist.design/","Web","Free","Check resource-specific terms","ux,checklist"),
("Laws of UX","UX Learning","UX principles and design guidance.","https://lawsofux.com/","Web","Free","Check current terms","ux,learning"),
("Coolors","Colour Tools","Generate and explore colour palettes.","https://coolors.co/","Web","Free + paid","Check export and commercial terms","colour,palette"),
("WebAIM Contrast Checker","Accessibility","Check foreground/background contrast.","https://webaim.org/resources/contrastchecker/","Web","Free","Use alongside accessibility guidance","accessibility,contrast"),
]
class CatalogService:
    def __init__(self, path):
        self.path = str(path); Path(self.path).parent.mkdir(parents=True, exist_ok=True); self.init_db()
    def connect(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; return c
    def init_db(self):
        with self.connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS resources(id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, description TEXT DEFAULT '', url TEXT NOT NULL, platform TEXT DEFAULT 'Web', pricing TEXT DEFAULT 'Unknown', licence TEXT DEFAULT 'Check provider', status TEXT DEFAULT 'Not checked', tags TEXT DEFAULT '', favorite INTEGER DEFAULT 0, notes TEXT DEFAULT '')""")
            if c.execute("SELECT COUNT(*) FROM resources").fetchone()[0] == 0:
                c.executemany("INSERT INTO resources(name,category,description,url,platform,pricing,licence,tags) VALUES(?,?,?,?,?,?,?,?)", SEED)
    def list(self, search="", category="All", platform="All", pricing="All", status="All", favorites=False):
        sql="SELECT * FROM resources WHERE 1=1"; args=[]
        if search.strip():
            q=f"%{search.strip()}%"; sql+=" AND (name LIKE ? OR category LIKE ? OR description LIKE ? OR url LIKE ? OR tags LIKE ? OR notes LIKE ?)"; args += [q]*6
        for col,val in [("category",category),("platform",platform),("pricing",pricing),("status",status)]:
            if val != "All": sql+=f" AND {col}=?"; args.append(val)
        if favorites: sql+=" AND favorite=1"
        sql+=" ORDER BY favorite DESC, category COLLATE NOCASE, name COLLATE NOCASE"
        with self.connect() as c: rows=c.execute(sql,args).fetchall()
        return [Resource(**{**dict(r),"favorite":bool(r["favorite"])}) for r in rows]
    def get(self, rid):
        with self.connect() as c: r=c.execute("SELECT * FROM resources WHERE id=?",(rid,)).fetchone()
        return Resource(**{**dict(r),"favorite":bool(r["favorite"])}) if r else None
    def save(self,r):
        if not r.name.strip(): raise ValueError("Resource name is required.")
        u=urlparse(r.url.strip())
        if u.scheme not in ("http","https") or not u.netloc: raise ValueError("Enter a valid http:// or https:// URL.")
        vals=(r.name.strip(),r.category,r.description.strip(),r.url.strip(),r.platform,r.pricing,r.licence,r.status,r.tags,r.favorite and 1 or 0,r.notes)
        with self.connect() as c:
            if r.id is None:
                cur=c.execute("INSERT INTO resources(name,category,description,url,platform,pricing,licence,status,tags,favorite,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",vals); return cur.lastrowid
            c.execute("UPDATE resources SET name=?,category=?,description=?,url=?,platform=?,pricing=?,licence=?,status=?,tags=?,favorite=?,notes=? WHERE id=?",vals+(r.id,)); return r.id
    def delete(self,rid):
        with self.connect() as c: c.execute("DELETE FROM resources WHERE id=?",(rid,))
    def toggle(self,rid):
        with self.connect() as c: c.execute("UPDATE resources SET favorite=1-favorite WHERE id=?",(rid,))
    def categories(self):
        with self.connect() as c: return [r[0] for r in c.execute("SELECT DISTINCT category FROM resources ORDER BY category")]
    def export(self,path):
        rows=self.list()
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f); w.writerow(["ID","Name","Category","Description","URL","Platform","Pricing","Licence","Status","Tags","Favourite","Notes"])
            for r in rows: w.writerow([r.id,r.name,r.category,r.description,r.url,r.platform,r.pricing,r.licence,r.status,r.tags,r.favorite,r.notes])
        return len(rows)
