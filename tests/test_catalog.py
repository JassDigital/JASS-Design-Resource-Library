from jass_design_resource_library.models import Resource
from jass_design_resource_library.services import CatalogService

def test_seed_and_search(tmp_path):
    s=CatalogService(tmp_path/"test.sqlite3")
    assert len(s.list()) >= 20
    assert s.list(search="Lucide")[0].name == "Lucide"

def test_add_edit_favorite_delete(tmp_path):
    s=CatalogService(tmp_path/"test.sqlite3")
    r=Resource(name="Example",url="https://example.com")
    rid=s.save(r); assert s.get(rid).name=="Example"
    r.id=rid; r.name="Edited"; s.save(r); s.toggle(rid)
    assert s.get(rid).favorite and s.get(rid).name=="Edited"
    s.delete(rid); assert s.get(rid) is None

def test_validation(tmp_path):
    s=CatalogService(tmp_path/"test.sqlite3")
    for r in [Resource(name="",url="https://example.com"),Resource(name="Bad",url="javascript:alert(1)")]:
        try:s.save(r); assert False
        except ValueError:pass

def test_export_csv(tmp_path):
    s=CatalogService(tmp_path/"test.sqlite3"); p=tmp_path/"export.csv"
    assert s.export(p)>=20
    assert "Google Fonts" in p.read_text(encoding="utf-8-sig")
