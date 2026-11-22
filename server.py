"""API REST local para a demonstração acadêmica Aurora Saúde."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
DB = ROOT / "aurora.sqlite3"
HOST, PORT = "127.0.0.1", 4173


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS doctors (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, specialty TEXT NOT NULL,
          start TEXT NOT NULL, end TEXT NOT NULL, step INTEGER NOT NULL,
          days TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS patients (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL,
          email TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS appointments (
          id TEXT PRIMARY KEY,
          patient_id TEXT NOT NULL REFERENCES patients(id),
          doctor_id TEXT NOT NULL REFERENCES doctors(id),
          date TEXT NOT NULL, time TEXT NOT NULL,
          status TEXT NOT NULL CHECK(status IN ('Agendada','Cancelada','Concluída'))
        );
        CREATE UNIQUE INDEX IF NOT EXISTS one_active_visit_per_slot
          ON appointments(doctor_id,date,time) WHERE status='Agendada';
        CREATE TABLE IF NOT EXISTS activity (
          id TEXT PRIMARY KEY, text TEXT NOT NULL, at TEXT NOT NULL
        );
        """)
        if con.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
            con.executemany("INSERT INTO doctors VALUES(?,?,?,?,?,?,?)", [
                ("d1", "Dra. Helena Costa", "Clínica geral", "08:00", "17:00", 30, "[1,2,3,4,5]"),
                ("d2", "Dr. Rafael Martins", "Cardiologia", "09:00", "18:00", 30, "[1,2,3,4,5]"),
                ("d3", "Dra. Camila Rocha", "Dermatologia", "08:30", "16:30", 30, "[1,2,3,4,5]"),
            ])
        if con.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
            con.executemany("INSERT INTO patients VALUES(?,?,?,?)", [
                ("p1", "Mariana Alves", "(11) 98812-3040", "mariana@email.com"),
                ("p2", "Lucas Ferreira", "(11) 97723-1548", "lucas@email.com"),
                ("p3", "Beatriz Nunes", "(11) 96634-2091", "beatriz@email.com"),
            ])
        if con.execute("SELECT COUNT(*) FROM activity").fetchone()[0] == 0:
            con.execute("INSERT INTO activity VALUES(?,?,?)", (
                "n1", "API Aurora iniciada. Dados fictícios carregados.", datetime.now().astimezone().isoformat(timespec="minutes")
            ))


def state_from_db(con):
    doctors = []
    for row in con.execute("SELECT * FROM doctors ORDER BY name"):
        item = dict(row)
        item["step"] = int(item["step"])
        item["days"] = json.loads(item["days"])
        doctors.append(item)
    return {
        "doctors": doctors,
        "patients": [dict(r) for r in con.execute("SELECT * FROM patients ORDER BY name")],
        "appointments": [dict(r) for r in con.execute("SELECT id,patient_id AS patientId,doctor_id AS doctorId,date,time,status FROM appointments ORDER BY date,time")],
        "notes": [dict(r) for r in con.execute("SELECT id,text,at FROM activity ORDER BY at DESC LIMIT 8")],
    }


def validate_booking(con, payload, skip_id=None):
    required = ("patientId", "doctorId", "date", "time")
    if any(not payload.get(key) for key in required):
        raise ValueError("Informe paciente, profissional, data e horário.")
    patient = con.execute("SELECT id FROM patients WHERE id=?", (payload["patientId"],)).fetchone()
    doctor = con.execute("SELECT * FROM doctors WHERE id=?", (payload["doctorId"],)).fetchone()
    if not patient or not doctor:
        raise ValueError("Paciente ou profissional não encontrado.")
    try:
        starts = datetime.strptime(payload["date"] + "T" + payload["time"], "%Y-%m-%dT%H:%M")
    except ValueError as exc:
        raise ValueError("Data ou horário inválido.") from exc
    if starts < datetime.now() + timedelta(hours=24):
        raise ValueError("A consulta exige pelo menos 24 horas de antecedência.")
    days = json.loads(doctor["days"])
    if starts.weekday() not in days:
        raise ValueError("O profissional não atende neste dia da semana.")
    minute = starts.hour * 60 + starts.minute
    sh, sm = map(int, doctor["start"].split(":"))
    eh, em = map(int, doctor["end"].split(":"))
    first, last = sh * 60 + sm, eh * 60 + em
    step = int(doctor["step"])
    if minute < first or minute + step > last or (minute - first) % step:
        raise ValueError("O horário não pertence à disponibilidade configurada.")
    sql = "SELECT id FROM appointments WHERE doctor_id=? AND date=? AND time=? AND status='Agendada'"
    args = [payload["doctorId"], payload["date"], payload["time"]]
    if skip_id:
        sql += " AND id<>?"
        args.append(skip_id)
    if con.execute(sql, args).fetchone():
        raise ValueError("Este horário já está reservado.")


DOCS = """<!doctype html><html lang='pt-BR'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Documentação da API Aurora</title><style>
body{margin:0;background:#f4f7f5;color:#19343d;font:15px/1.5 system-ui,Segoe UI,sans-serif}.wrap{max-width:970px;margin:38px auto;padding:0 20px}h1{margin:0 0 6px}p{color:#71858a}.top{background:#183b46;color:#fff;padding:26px 30px;border-radius:16px}.top p{color:#c5d8d7;margin:4px 0}.box{background:#fff;border:1px solid #e1eae8;border-radius:12px;padding:19px 20px;margin-top:14px}.route{display:flex;align-items:center;gap:12px;border-top:1px solid #edf0f1;padding:14px 0}.route:first-of-type{border-top:0}.verb{background:#e4f3ef;color:#14766f;border-radius:6px;padding:4px 8px;font:700 11px ui-monospace,monospace}.path{font:600 13px ui-monospace,monospace}.desc{color:#6d7e84;font-size:12px;flex:1}.call{border:0;background:#157a74;color:white;border-radius:7px;padding:7px 10px;font-size:11px;cursor:pointer}.out{background:#152b33;color:#c8ece4;border-radius:10px;padding:14px;min-height:60px;white-space:pre-wrap;overflow:auto;font:12px/1.5 ui-monospace,monospace}.foot{font-size:11px}.ok{color:#7ce0a6}.bad{color:#ff9b9b}</style>
<body><main class='wrap'><header class='top'><h1>API de agendamento Aurora</h1><p>REST local · SQLite · JSON · validação de disponibilidade e prazos</p></header>
<section class='box'><h2>Rotas disponíveis</h2>
<div class='route'><b class='verb'>GET</b><code class='path'>/api/health</code><span class='desc'>Estado do serviço</span><button class='call' data-url='/api/health'>Executar</button></div>
<div class='route'><b class='verb'>GET</b><code class='path'>/api/state</code><span class='desc'>Lê o estado atual da clínica</span><button class='call' data-url='/api/state'>Executar</button></div>
<div class='route'><b class='verb'>PUT</b><code class='path'>/api/state</code><span class='desc'>Sincroniza alterações do painel</span><span class='badge'>JSON</span></div>
<div class='route'><b class='verb'>GET</b><code class='path'>/api/doctors</code><span class='desc'>Lista profissionais e disponibilidade</span><button class='call' data-url='/api/doctors'>Executar</button></div>
<div class='route'><b class='verb'>GET</b><code class='path'>/api/patients</code><span class='desc'>Lista pacientes da demonstração</span><button class='call' data-url='/api/patients'>Executar</button></div>
<div class='route'><b class='verb'>GET</b><code class='path'>/api/appointments</code><span class='desc'>Lista consultas; aceita filtro ?date=AAAA-MM-DD</span><button class='call' data-url='/api/appointments?date=2026-11-25'>Executar</button></div>
<div class='route'><b class='verb'>POST</b><code class='path'>/api/appointments</code><span class='desc'>Cria consulta e valida a regra de 24 horas</span><button class='call' data-url='/api/appointments?demo=1'>Executar exemplo</button></div><div class='route'><b class='verb'>PATCH</b><code class='path'>/api/appointments/{id}</code><span class='desc'>Cancela ou reagenda uma consulta</span><span class='badge'>JSON</span></div></section>
<section class='box'><h2>Resposta da API</h2><pre class='out' id='out'>Escolha uma rota para executar a chamada.</pre><p class='foot'>Os exemplos usam cadastros fictícios e ficam no banco local aurora.sqlite3.</p></section>
<script>document.querySelectorAll('[data-url]').forEach(b=>b.onclick=async()=>{const out=document.querySelector('#out');out.textContent='Enviando requisição...';try{let url=b.dataset.url,method='GET',body;if(url.endsWith('?demo=1')){url='/api/appointments';method='POST';const doctors=await(await fetch('/api/doctors')).json(),patients=await(await fetch('/api/patients')).json();const d=doctors[0],p=patients[0];let day=new Date(Date.now()+72*3600000);while(day.getDay()===0||day.getDay()===6)day.setDate(day.getDate()+1);let hm=d.start.split(':').map(Number),date=day.toISOString().slice(0,10),time=d.start;body={patientId:p.id,doctorId:d.id,date,time}}const res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined}),json=await res.json();out.textContent=`${method} ${url}\nHTTP ${res.status}\n\n${JSON.stringify(json,null,2)}`}catch(e){out.textContent='Falha na chamada: '+e.message}});</script></main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "AuroraAPI/1.0"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.log_date_time_string(), fmt % args))

    def send_body(self, status, body, content_type="application/json; charset=utf-8"):
        raw = body.encode("utf-8") if isinstance(body, str) else json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        size = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(size) or b"{}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/docs":
            return self.send_body(200, DOCS, "text/html; charset=utf-8")
        if parsed.path == "/api/health":
            return self.send_body(200, {"status": "ok", "service": "aurora-agenda-api", "version": "1.0.0"})
        with connect() as con:
            if parsed.path == "/api/state":
                return self.send_body(200, state_from_db(con))
            if parsed.path == "/api/doctors":
                return self.send_body(200, state_from_db(con)["doctors"])
            if parsed.path == "/api/patients":
                return self.send_body(200, state_from_db(con)["patients"])
            if parsed.path == "/api/appointments":
                day = parse_qs(parsed.query).get("date", [None])[0]
                items = state_from_db(con)["appointments"]
                if day:
                    items = [a for a in items if a["date"] == day]
                return self.send_body(200, items)
        if parsed.path == "/assets/aurora-logo.svg":
            return self.send_body(200, (ROOT / "assets" / "aurora-logo.svg").read_text(encoding="utf-8"), "image/svg+xml; charset=utf-8")
        if parsed.path == "/" or parsed.path == "/index.html":
            return self.send_body(200, (ROOT / "index.html").read_text(encoding="utf-8-sig"), "text/html; charset=utf-8")
        return self.send_body(404, {"error": "Rota não encontrada"})

    def do_PUT(self):
        if urlparse(self.path).path != "/api/state":
            return self.send_body(404, {"error": "Rota não encontrada"})
        try:
            payload = self.read_json()
            with connect() as con:
                con.execute("BEGIN")
                con.execute("DELETE FROM appointments")
                con.execute("DELETE FROM activity")
                con.execute("DELETE FROM patients")
                con.execute("DELETE FROM doctors")
                for d in payload.get("doctors", []):
                    con.execute("INSERT INTO doctors VALUES(?,?,?,?,?,?,?)", (d["id"],d["name"],d["specialty"],d["start"],d["end"],int(d["step"]),json.dumps(d["days"])))
                for p in payload.get("patients", []):
                    con.execute("INSERT INTO patients VALUES(?,?,?,?)", (p["id"],p["name"],p["phone"],p["email"]))
                for a in payload.get("appointments", []):
                    con.execute("INSERT INTO appointments VALUES(?,?,?,?,?,?)", (a["id"],a["patientId"],a["doctorId"],a["date"],a["time"],a["status"]))
                for n in payload.get("notes", [])[:8]:
                    con.execute("INSERT INTO activity VALUES(?,?,?)", (n["id"],n["text"],n["at"]))
                result = state_from_db(con)
            self.send_body(200, {"saved": True, "counts": {k:len(v) for k,v in result.items()}})
        except (ValueError, KeyError, sqlite3.Error, json.JSONDecodeError) as exc:
            self.send_body(400, {"error": str(exc)})

    def do_POST(self):
        if urlparse(self.path).path != "/api/appointments":
            return self.send_body(404, {"error": "Rota não encontrada"})
        try:
            payload = self.read_json()
            with connect() as con:
                validate_booking(con, payload)
                item = {"id":str(uuid4()), **{key:payload[key] for key in ("patientId","doctorId","date","time")}, "status":"Agendada"}
                con.execute("INSERT INTO appointments VALUES(?,?,?,?,?,?)", (item["id"],item["patientId"],item["doctorId"],item["date"],item["time"],item["status"]))
            self.send_body(201, item)
        except (ValueError, KeyError, sqlite3.Error, json.JSONDecodeError) as exc:
            self.send_body(400, {"error": str(exc)})

    def do_PATCH(self):
        path = urlparse(self.path).path
        prefix = "/api/appointments/"
        if not path.startswith(prefix):
            return self.send_body(404, {"error": "Rota não encontrada"})
        appointment_id = path[len(prefix):]
        try:
            payload = self.read_json()
            with connect() as con:
                row = con.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
                if not row:
                    return self.send_body(404, {"error": "Consulta não encontrada"})
                if payload.get("status") == "Cancelada":
                    con.execute("UPDATE appointments SET status='Cancelada' WHERE id=?", (appointment_id,))
                elif payload.get("date") and payload.get("time"):
                    merged = {"patientId":row["patient_id"],"doctorId":row["doctor_id"],"date":payload["date"],"time":payload["time"]}
                    validate_booking(con, merged, skip_id=appointment_id)
                    con.execute("UPDATE appointments SET date=?,time=? WHERE id=?", (merged["date"],merged["time"],appointment_id))
                else:
                    return self.send_body(400, {"error": "Informe status de cancelamento ou nova data e horário."})
                updated = con.execute("SELECT id,patient_id AS patientId,doctor_id AS doctorId,date,time,status FROM appointments WHERE id=?", (appointment_id,)).fetchone()
            self.send_body(200, dict(updated))
        except (ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
            self.send_body(400, {"error": str(exc)})


if __name__ == "__main__":
    init_db()
    print(f"Aurora API pronta em http://{HOST}:{PORT}/api/docs")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
