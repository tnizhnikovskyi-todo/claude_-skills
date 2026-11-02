from shop.cli import main

CSV = """number,customer,status,created,amount
A1,Acme,paid,2026-01-10,100.0
A2,Beta,draft,2026-02-15,50.5
A3,Acme,paid,2026-03-01,10.0
"""


def test_status_filter(tmp_path, capsys):
    p = tmp_path / "orders.csv"
    p.write_text(CSV, encoding="utf-8")
    assert main([str(p), "--status", "paid"]) == 0
    out = capsys.readouterr().out
    assert "A1" in out and "A3" in out and "A2" not in out
