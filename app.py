from flask import Flask, render_template, request, jsonify
from datetime import date, datetime
import sqlite3, os, difflib

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "smartpharm.db")
app = Flask(__name__)

SEED = [
    ("Paracetamol 500 mg","Paracetamol","Analgesic / antipyretic","Tablet","Pain and fever relief","Do not exceed the recommended dose."),
    ("Ibuprofen 200 mg","Ibuprofen","NSAID","Tablet","Pain, inflammation and fever","Use caution with stomach/kidney problems."),
    ("Aspirin 100 mg","Acetylsalicylic acid","Antiplatelet / NSAID","Tablet","Antiplatelet therapy","Bleeding risk; use only as directed."),
    ("Amoxicillin 500 mg","Amoxicillin","Penicillin antibiotic","Capsule","Bacterial infections","Use antibiotics only as directed by a qualified professional."),
    ("Cetirizine 10 mg","Cetirizine","Antihistamine","Tablet","Allergic symptoms","May cause drowsiness in some people."),
]

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, ingredient TEXT NOT NULL, group_name TEXT NOT NULL,
        form TEXT NOT NULL, indication TEXT NOT NULL, warning TEXT NOT NULL)""")
    if c.execute("SELECT COUNT(*) FROM medicines").fetchone()[0] == 0:
        c.executemany("""INSERT INTO medicines
        (name,ingredient,group_name,form,indication,warning) VALUES (?,?,?,?,?,?)""", SEED)
    c.commit(); c.close()

init_db()

@app.route("/")
def home():
    c=db()
    medicines=c.execute("SELECT * FROM medicines ORDER BY name").fetchall()
    c.close()
    return render_template("index.html", medicines=medicines)

@app.get("/api/search")
def search():
    q=request.args.get("q","").strip().lower()
    c=db()
    if q:
        rows=c.execute("""SELECT * FROM medicines
        WHERE lower(name) LIKE ? OR lower(ingredient) LIKE ? OR lower(group_name) LIKE ?
        ORDER BY name LIMIT 50""",(f"%{q}%",f"%{q}%",f"%{q}%")).fetchall()
    else:
        rows=c.execute("SELECT * FROM medicines ORDER BY name LIMIT 50").fetchall()
    c.close()
    return jsonify([dict(x) for x in rows])

@app.get("/api/medicine/<int:mid>")
def medicine(mid):
    c=db(); row=c.execute("SELECT * FROM medicines WHERE id=?",(mid,)).fetchone(); c.close()
    return (jsonify(dict(row)) if row else (jsonify({"error":"Not found"}),404))

@app.post("/api/interaction")
def interaction():
    d=request.get_json(force=True)
    a,b=int(d.get("a",0)),int(d.get("b",0))
    if a==b:
        return jsonify({"level":"info","title":"Bir xil preparat","text":"Bir xil preparat tanlandi."})
    # Demo signals only; production must use validated clinical sources.
    pair=tuple(sorted((a,b)))
    signals={
        (1,2):("warning","Tekshirish kerak","Bu demo signal. Rasmiy klinik manba va mutaxassis bilan tekshirilishi kerak."),
        (2,3):("warning","Ehtiyotkorlik","Bu demo signal. Rasmiy klinik manba va mutaxassis bilan tekshirilishi kerak.")
    }
    x=signals.get(pair,("info","Bazadagi signal yo‘q","Bu xavfsiz degani emas. Rasmiy manbani tekshiring."))
    return jsonify({"level":x[0],"title":x[1],"text":x[2]})

@app.post("/api/expiry")
def expiry():
    try:
        d=request.get_json(force=True)
        days=(datetime.strptime(d["expiry"],"%Y-%m-%d").date()-date.today()).days
        return jsonify({"days":days,"status":"expired" if days<0 else "soon" if days<=30 else "valid"})
    except Exception:
        return jsonify({"error":"Sana noto‘g‘ri"}),400

@app.post("/api/lasa")
def lasa():
    d=request.get_json(force=True); mid=int(d.get("id",0))
    c=db(); m=c.execute("SELECT * FROM medicines WHERE id=?",(mid,)).fetchone()
    rows=c.execute("SELECT * FROM medicines WHERE id!=?",(mid,)).fetchall(); c.close()
    if not m: return jsonify({"error":"Not found"}),404
    similar=sorted(rows,key=lambda x:difflib.SequenceMatcher(None,m["name"].lower(),x["name"].lower()).ratio(),reverse=True)[:3]
    return jsonify({"message":"LASA natijalari ekspert validatsiyasidan o‘tkazilishi kerak.","similar":[dict(x) for x in similar]})

@app.get("/health")
def health():
    return jsonify({"status":"ok","service":"SmartPharm"})

if __name__=="__main__":
    port=int(os.environ.get("PORT","5000"))
    app.run(host="0.0.0.0",port=port)
