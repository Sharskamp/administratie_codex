import csv
import sqlite3
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime, date
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote
import webbrowser

DB_PATH = "admin_data.db"
DATE_FMT = "%Y-%m-%d"
DT_FMT = "%Y-%m-%d %H:%M"


@dataclass
class ValidationResult:
    ok: bool
    message: str = ""


class DB:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.migrate()
        self.seed_defaults()

    def create_tables(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id=1),
                company_name TEXT,
                company_email TEXT,
                company_iban TEXT,
                company_kvk TEXT,
                vat_rate REAL DEFAULT 21,
                google_client_path TEXT,
                google_connected INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                postal_code TEXT,
                btw_number TEXT,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                start_at TEXT,
                end_at TEXT,
                hours REAL DEFAULT 1,
                hourly_rate REAL DEFAULT 0,
                billable INTEGER DEFAULT 1,
                invoiced INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );

            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                issue_date TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'concept',
                scheduled_send_at TEXT,
                paid_at TEXT,
                subtotal REAL DEFAULT 0,
                vat_rate REAL DEFAULT 21,
                vat_amount REAL DEFAULT 0,
                total REAL DEFAULT 0,
                notes TEXT,
                created_at TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );

            CREATE TABLE IF NOT EXISTS invoice_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                appointment_id INTEGER,
                description TEXT NOT NULL,
                quantity REAL DEFAULT 1,
                unit_price REAL DEFAULT 0,
                line_total REAL DEFAULT 0,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id),
                FOREIGN KEY(appointment_id) REFERENCES appointments(id)
            );

            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                account_ref TEXT,
                reference TEXT,
                invoice_id INTEGER,
                matched INTEGER DEFAULT 0,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            );

            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                supplier TEXT,
                amount_excl REAL DEFAULT 0,
                vat_amount REAL DEFAULT 0,
                amount_incl REAL DEFAULT 0,
                category_id INTEGER,
                receipt_path TEXT,
                notes TEXT,
                FOREIGN KEY(category_id) REFERENCES expense_categories(id)
            );
            """
        )
        self.conn.commit()

    def migrate(self):
        cols = [r[1] for r in self.q("PRAGMA table_info(settings)").fetchall()]
        if "company_iban" not in cols:
            self.q("ALTER TABLE settings ADD COLUMN company_iban TEXT")
        if "company_kvk" not in cols:
            self.q("ALTER TABLE settings ADD COLUMN company_kvk TEXT")
        if "vat_rate" not in cols:
            self.q("ALTER TABLE settings ADD COLUMN vat_rate REAL DEFAULT 21")

    def seed_defaults(self):
        self.q("INSERT OR IGNORE INTO settings (id, google_connected) VALUES (1, 0)")
        self.q("UPDATE settings SET vat_rate = COALESCE(vat_rate, 21) WHERE id=1")
        for cat in ["Software", "Reiskosten", "Kantoor", "Marketing", "Overig"]:
            self.q("INSERT OR IGNORE INTO expense_categories(name) VALUES(?)", (cat,))

    def q(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZZP Administratie Pro (Windows)")
        self.geometry("1280x780")
        self.db = DB()

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True)

        self.tab_settings = ttk.Frame(tabs)
        self.tab_customers = ttk.Frame(tabs)
        self.tab_agenda = ttk.Frame(tabs)
        self.tab_invoices = ttk.Frame(tabs)
        self.tab_income = ttk.Frame(tabs)
        self.tab_expense = ttk.Frame(tabs)
        self.tab_report = ttk.Frame(tabs)

        tabs.add(self.tab_settings, text="Instellingen")
        tabs.add(self.tab_customers, text="Klanten")
        tabs.add(self.tab_agenda, text="Agenda")
        tabs.add(self.tab_invoices, text="Facturen")
        tabs.add(self.tab_income, text="Inkomsten")
        tabs.add(self.tab_expense, text="Uitgaven")
        tabs.add(self.tab_report, text="Dashboard")

        self.build_settings()
        self.build_customers()
        self.build_agenda()
        self.build_invoices()
        self.build_income()
        self.build_expense()
        self.build_report()

    def _entry(self, parent, label, r, default="", w=40):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", padx=4, pady=4)
        e = ttk.Entry(parent, width=w)
        e.insert(0, default)
        e.grid(row=r, column=1, sticky="w", padx=4, pady=4)
        return e

    def build_settings(self):
        frm = ttk.LabelFrame(self.tab_settings, text="Bedrijfsgegevens", padding=10)
        frm.pack(fill="x", padx=10, pady=10)
        self.s_name = self._entry(frm, "Bedrijfsnaam", 0)
        self.s_email = self._entry(frm, "E-mail", 1)
        self.s_iban = self._entry(frm, "IBAN", 2)
        self.s_kvk = self._entry(frm, "KvK", 3)
        self.s_vat = self._entry(frm, "BTW %", 4, "21")
        self.s_google = self._entry(frm, "Google client secret JSON", 5, "")
        ttk.Button(frm, text="Bestand kiezen", command=self.pick_google).grid(row=5, column=2)
        self.google_label = ttk.Label(frm, text="Google status: niet gekoppeld")
        self.google_label.grid(row=6, column=1, sticky="w")
        ttk.Button(frm, text="Opslaan", command=self.save_settings).grid(row=7, column=1, sticky="w")

    def build_customers(self):
        frm = ttk.Frame(self.tab_customers, padding=8)
        frm.pack(fill="both", expand=True)
        form = ttk.LabelFrame(frm, text="Klant", padding=8)
        form.pack(fill="x")
        self.c_name = self._entry(form, "Naam", 0)
        self.c_email = self._entry(form, "E-mail", 1)
        self.c_phone = self._entry(form, "Telefoon", 2)
        self.c_address = self._entry(form, "Adres", 3)
        self.c_city = self._entry(form, "Plaats", 4)
        self.c_post = self._entry(form, "Postcode", 5)
        self.c_btw = self._entry(form, "BTW nummer", 6)
        ttk.Button(form, text="Klant opslaan", command=self.add_customer).grid(row=7, column=1, sticky="w")
        self.customer_tree = ttk.Treeview(frm, columns=("id", "name", "email", "phone", "city"), show="headings", height=16)
        for c in ("id", "name", "email", "phone", "city"):
            self.customer_tree.heading(c, text=c)
        self.customer_tree.pack(fill="both", expand=True, pady=8)

    def build_agenda(self):
        frm = ttk.Frame(self.tab_agenda, padding=8)
        frm.pack(fill="both", expand=True)
        f = ttk.LabelFrame(frm, text="Afspraak", padding=8)
        f.pack(fill="x")
        ttk.Label(f, text="Klant").grid(row=0, column=0, sticky="w")
        self.a_customer = ttk.Combobox(f, width=58, state="readonly")
        self.a_customer.grid(row=0, column=1, sticky="w")
        self.a_title = self._entry(f, "Titel", 1)
        self.a_start = self._entry(f, "Start (YYYY-MM-DD HH:MM)", 2)
        self.a_end = self._entry(f, "Einde (YYYY-MM-DD HH:MM)", 3)
        self.a_hours = self._entry(f, "Uren", 4, "1")
        self.a_rate = self._entry(f, "Tarief p/u", 5, "75")
        ttk.Button(f, text="Afspraak opslaan", command=self.add_appointment).grid(row=6, column=1, sticky="w")
        self.agenda_tree = ttk.Treeview(frm, columns=("id", "customer", "title", "start", "hours", "rate", "invoiced"), show="headings", height=16)
        for c in ("id", "customer", "title", "start", "hours", "rate", "invoiced"):
            self.agenda_tree.heading(c, text=c)
        self.agenda_tree.pack(fill="both", expand=True, pady=8)

    def build_invoices(self):
        frm = ttk.Frame(self.tab_invoices, padding=8)
        frm.pack(fill="both", expand=True)
        top = ttk.LabelFrame(frm, text="Factuur aanmaken", padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Klant").grid(row=0, column=0, sticky="w")
        self.i_customer = ttk.Combobox(top, width=58, state="readonly")
        self.i_customer.grid(row=0, column=1, sticky="w")
        ttk.Button(top, text="Nieuwe lege factuur", command=self.create_blank_invoice).grid(row=0, column=2, padx=5)

        ttk.Label(top, text="Afspraken (nog niet gefactureerd)").grid(row=1, column=0, sticky="nw")
        self.i_appt_list = tk.Listbox(top, selectmode=tk.MULTIPLE, width=90, height=6)
        self.i_appt_list.grid(row=1, column=1, columnspan=2, sticky="w")
        ttk.Button(top, text="Maak factuur uit selectie", command=self.create_invoice_from_selected_appointments).grid(row=2, column=1, sticky="w", pady=4)

        self.inv_tree = ttk.Treeview(frm, columns=("id", "invoice_no", "customer", "issue", "due", "total", "status"), show="headings", height=12)
        for c in ("id", "invoice_no", "customer", "issue", "due", "total", "status"):
            self.inv_tree.heading(c, text=c)
        self.inv_tree.pack(fill="both", expand=True, pady=6)

        actions = ttk.Frame(frm)
        actions.pack(fill="x")
        ttk.Button(actions, text="Bevestigen", command=lambda: self.set_invoice_status("bevestigd")).pack(side="left", padx=4)
        ttk.Button(actions, text="Markeer betaald", command=self.mark_paid).pack(side="left", padx=4)
        ttk.Button(actions, text="Verstuur e-mail", command=self.send_invoice_email).pack(side="left", padx=4)
        ttk.Button(actions, text="Verstuur WhatsApp", command=self.send_invoice_whatsapp).pack(side="left", padx=4)
        ttk.Button(actions, text="CSV export", command=self.export_invoice_csv).pack(side="left", padx=4)

    def build_income(self):
        frm = ttk.Frame(self.tab_income, padding=8)
        frm.pack(fill="both", expand=True)
        form = ttk.LabelFrame(frm, text="Inkomst", padding=8)
        form.pack(fill="x")
        self.in_date = self._entry(form, "Datum", 0, date.today().isoformat())
        self.in_amount = self._entry(form, "Bedrag", 1)
        self.in_account = self._entry(form, "Rekening referentie", 2)
        self.in_ref = self._entry(form, "Omschrijving", 3)
        ttk.Label(form, text="Factuur").grid(row=4, column=0, sticky="w")
        self.in_invoice = ttk.Combobox(form, width=58, state="readonly")
        self.in_invoice.grid(row=4, column=1, sticky="w")
        ttk.Button(form, text="Inkomst opslaan", command=self.add_income).grid(row=5, column=1, sticky="w")
        ttk.Button(form, text="Auto-match op factuurnummer", command=self.auto_match_incomes).grid(row=5, column=2, sticky="w")

        self.in_tree = ttk.Treeview(frm, columns=("id", "date", "amount", "reference", "invoice", "matched"), show="headings", height=16)
        for c in ("id", "date", "amount", "reference", "invoice", "matched"):
            self.in_tree.heading(c, text=c)
        self.in_tree.pack(fill="both", expand=True, pady=6)

    def build_expense(self):
        frm = ttk.Frame(self.tab_expense, padding=8)
        frm.pack(fill="both", expand=True)
        form = ttk.LabelFrame(frm, text="Uitgave", padding=8)
        form.pack(fill="x")
        self.ex_date = self._entry(form, "Datum", 0, date.today().isoformat())
        self.ex_supplier = self._entry(form, "Leverancier", 1)
        self.ex_excl = self._entry(form, "Bedrag excl.", 2, "0")
        self.ex_vat = self._entry(form, "BTW", 3, "0")
        self.ex_incl = self._entry(form, "Bedrag incl.", 4, "0")
        ttk.Label(form, text="Categorie").grid(row=5, column=0, sticky="w")
        self.ex_cat = ttk.Combobox(form, width=58, state="readonly")
        self.ex_cat.grid(row=5, column=1, sticky="w")
        self.ex_receipt = self._entry(form, "Bon bestand", 6)
        ttk.Button(form, text="Kies bestand", command=self.pick_receipt).grid(row=6, column=2)
        self.ex_notes = self._entry(form, "Notities", 7)
        ttk.Button(form, text="Uitgave opslaan", command=self.add_expense).grid(row=8, column=1, sticky="w")

        self.ex_tree = ttk.Treeview(frm, columns=("id", "date", "supplier", "incl", "category", "receipt"), show="headings", height=16)
        for c in ("id", "date", "supplier", "incl", "category", "receipt"):
            self.ex_tree.heading(c, text=c)
        self.ex_tree.pack(fill="both", expand=True, pady=6)

    def build_report(self):
        frm = ttk.Frame(self.tab_report, padding=8)
        frm.pack(fill="both", expand=True)
        self.report = tk.Text(frm)
        self.report.pack(fill="both", expand=True)
        ttk.Button(frm, text="Ververs dashboard", command=self.refresh_report).pack(anchor="w", pady=4)

    def validate_date(self, value, with_time=False):
        try:
            datetime.strptime(value, DT_FMT if with_time else DATE_FMT)
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, f"Ongeldige datum{'tijd' if with_time else ''}: {value}")

    def pick_google(self):
        p = filedialog.askopenfilename(title="Kies Google OAuth client JSON")
        if p:
            self.s_google.delete(0, tk.END)
            self.s_google.insert(0, p)

    def save_settings(self):
        self.db.q(
            "UPDATE settings SET company_name=?, company_email=?, company_iban=?, company_kvk=?, vat_rate=?, google_client_path=?, google_connected=? WHERE id=1",
            (self.s_name.get(), self.s_email.get(), self.s_iban.get(), self.s_kvk.get(), float(self.s_vat.get() or 21), self.s_google.get(), 1 if self.s_google.get() else 0),
        )
        self.refresh_settings()
        messagebox.showinfo("Opgeslagen", "Instellingen opgeslagen")

    def add_customer(self):
        if not self.c_name.get().strip():
            return messagebox.showerror("Fout", "Klantnaam is verplicht")
        self.db.q(
            "INSERT INTO customers(name,email,phone,address,city,postal_code,btw_number) VALUES(?,?,?,?,?,?,?)",
            (self.c_name.get(), self.c_email.get(), self.c_phone.get(), self.c_address.get(), self.c_city.get(), self.c_post.get(), self.c_btw.get()),
        )
        self.refresh_customers()

    def add_appointment(self):
        if not self.a_customer.get():
            return messagebox.showerror("Fout", "Selecteer klant")
        if not self.validate_date(self.a_start.get(), True).ok:
            return messagebox.showerror("Fout", "Startdatum ongeldig")
        if self.a_end.get() and not self.validate_date(self.a_end.get(), True).ok:
            return messagebox.showerror("Fout", "Einddatum ongeldig")
        cid = int(self.a_customer.get().split(" - ")[0])
        self.db.q(
            "INSERT INTO appointments(customer_id,title,start_at,end_at,hours,hourly_rate,billable) VALUES(?,?,?,?,?,?,1)",
            (cid, self.a_title.get(), self.a_start.get(), self.a_end.get(), float(self.a_hours.get() or 0), float(self.a_rate.get() or 0)),
        )
        self.refresh_agenda()

    def next_invoice_no(self):
        y = datetime.now().strftime("%Y")
        row = self.db.q("SELECT COUNT(*) c FROM invoices WHERE invoice_no LIKE ?", (f"INV-{y}-%",)).fetchone()
        return f"INV-{y}-{row['c']+1:05d}"

    def create_blank_invoice(self):
        if not self.i_customer.get():
            return messagebox.showerror("Fout", "Selecteer klant")
        cid = int(self.i_customer.get().split(" - ")[0])
        issue = date.today().isoformat()
        due = date.fromordinal(date.today().toordinal() + 14).isoformat()
        vat = float(self.s_vat.get() or 21)
        self.db.q(
            "INSERT INTO invoices(invoice_no,customer_id,issue_date,due_date,status,subtotal,vat_rate,vat_amount,total,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (self.next_invoice_no(), cid, issue, due, "concept", 0, vat, 0, 0, datetime.now().isoformat(timespec="minutes")),
        )
        self.refresh_invoices()

    def create_invoice_from_selected_appointments(self):
        sels = self.i_appt_list.curselection()
        if not sels:
            return messagebox.showerror("Fout", "Selecteer afspraken")
        appt_ids = [int(self.i_appt_list.get(i).split(" | ")[0]) for i in sels]
        rows = self.db.q(
            f"SELECT a.*, c.id cid FROM appointments a JOIN customers c ON c.id=a.customer_id WHERE a.id IN ({','.join(['?']*len(appt_ids))})",
            tuple(appt_ids),
        ).fetchall()
        cid = rows[0]["cid"]
        issue = date.today().isoformat()
        due = date.fromordinal(date.today().toordinal() + 14).isoformat()
        vat = float(self.s_vat.get() or 21)
        invoice_no = self.next_invoice_no()
        cur = self.db.q(
            "INSERT INTO invoices(invoice_no,customer_id,issue_date,due_date,status,subtotal,vat_rate,vat_amount,total,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (invoice_no, cid, issue, due, "concept", 0, vat, 0, 0, datetime.now().isoformat(timespec="minutes")),
        )
        inv_id = cur.lastrowid
        subtotal = 0.0
        for r in rows:
            line_total = round((r["hours"] or 0) * (r["hourly_rate"] or 0), 2)
            subtotal += line_total
            self.db.q(
                "INSERT INTO invoice_lines(invoice_id,appointment_id,description,quantity,unit_price,line_total) VALUES(?,?,?,?,?,?)",
                (inv_id, r["id"], r["title"], r["hours"], r["hourly_rate"], line_total),
            )
            self.db.q("UPDATE appointments SET invoiced=1 WHERE id=?", (r["id"],))
        vat_amount = round(subtotal * vat / 100, 2)
        total = round(subtotal + vat_amount, 2)
        self.db.q("UPDATE invoices SET subtotal=?, vat_amount=?, total=? WHERE id=?", (subtotal, vat_amount, total, inv_id))
        self.refresh_all()

    def selected_invoice_id(self):
        sel = self.inv_tree.selection()
        if not sel:
            return None
        return int(self.inv_tree.item(sel[0], "values")[0])

    def set_invoice_status(self, status):
        iid = self.selected_invoice_id()
        if not iid:
            return
        self.db.q("UPDATE invoices SET status=? WHERE id=?", (status, iid))
        self.refresh_invoices()

    def mark_paid(self):
        iid = self.selected_invoice_id()
        if not iid:
            return
        self.db.q("UPDATE invoices SET status='betaald', paid_at=? WHERE id=?", (datetime.now().isoformat(timespec="minutes"), iid))
        self.refresh_invoices()

    def send_invoice_email(self):
        iid = self.selected_invoice_id()
        if not iid:
            return
        inv = self.db.q("SELECT i.invoice_no,i.total,c.name,c.email FROM invoices i JOIN customers c ON c.id=i.customer_id WHERE i.id=?", (iid,)).fetchone()
        if not inv["email"]:
            return messagebox.showerror("Fout", "Klant heeft geen e-mailadres")
        body = quote(f"Beste {inv['name']},\n\nHierbij factuur {inv['invoice_no']} van EUR {inv['total']:.2f}.\n")
        webbrowser.open(f"mailto:{inv['email']}?subject={quote('Factuur '+inv['invoice_no'])}&body={body}")
        self.db.q("UPDATE invoices SET status='verzonden' WHERE id=?", (iid,))
        self.refresh_invoices()

    def send_invoice_whatsapp(self):
        iid = self.selected_invoice_id()
        if not iid:
            return
        inv = self.db.q("SELECT i.invoice_no,i.total,c.phone FROM invoices i JOIN customers c ON c.id=i.customer_id WHERE i.id=?", (iid,)).fetchone()
        phone = "".join(ch for ch in (inv["phone"] or "") if ch.isdigit())
        if not phone:
            return messagebox.showerror("Fout", "Klant heeft geen telefoonnummer")
        msg = quote(f"Factuur {inv['invoice_no']} van EUR {inv['total']:.2f}")
        webbrowser.open(f"https://wa.me/{phone}?text={msg}")
        self.db.q("UPDATE invoices SET status='verzonden' WHERE id=?", (iid,))
        self.refresh_invoices()

    def export_invoice_csv(self):
        iid = self.selected_invoice_id()
        if not iid:
            return
        p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Exporteer factuur")
        if not p:
            return
        inv = self.db.q("SELECT * FROM invoices WHERE id=?", (iid,)).fetchone()
        lines = self.db.q("SELECT * FROM invoice_lines WHERE invoice_id=?", (iid,)).fetchall()
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Factuur", inv["invoice_no"], "Datum", inv["issue_date"], "Totaal", inv["total"]])
            w.writerow([])
            w.writerow(["Omschrijving", "Aantal", "Prijs", "Regel totaal"])
            for l in lines:
                w.writerow([l["description"], l["quantity"], l["unit_price"], l["line_total"]])
        messagebox.showinfo("Klaar", f"CSV opgeslagen: {p}")

    def add_income(self):
        if not self.validate_date(self.in_date.get()).ok:
            return messagebox.showerror("Fout", "Datum ongeldig")
        inv_id = int(self.in_invoice.get().split(" - ")[0]) if self.in_invoice.get() else None
        self.db.q(
            "INSERT INTO incomes(date,amount,account_ref,reference,invoice_id,matched) VALUES(?,?,?,?,?,?)",
            (self.in_date.get(), float(self.in_amount.get() or 0), self.in_account.get(), self.in_ref.get(), inv_id, 1 if inv_id else 0),
        )
        self.refresh_income()

    def auto_match_incomes(self):
        incomes = self.db.q("SELECT id,reference FROM incomes WHERE (invoice_id IS NULL OR matched=0)").fetchall()
        invoices = self.db.q("SELECT id,invoice_no,total FROM invoices").fetchall()
        matched = 0
        for inc in incomes:
            ref = inc["reference"] or ""
            for inv in invoices:
                if inv["invoice_no"] in ref:
                    self.db.q("UPDATE incomes SET invoice_id=?, matched=1 WHERE id=?", (inv["id"], inc["id"]))
                    matched += 1
                    break
        self.refresh_income()
        messagebox.showinfo("Auto-match", f"{matched} inkomsten gekoppeld")

    def pick_receipt(self):
        p = filedialog.askopenfilename(title="Kies bon")
        if p:
            self.ex_receipt.delete(0, tk.END)
            self.ex_receipt.insert(0, p)

    def add_expense(self):
        if not self.validate_date(self.ex_date.get()).ok:
            return messagebox.showerror("Fout", "Datum ongeldig")
        cat_name = self.ex_cat.get()
        cat = self.db.q("SELECT id FROM expense_categories WHERE name=?", (cat_name,)).fetchone()
        cat_id = cat["id"] if cat else None
        self.db.q(
            "INSERT INTO expenses(date,supplier,amount_excl,vat_amount,amount_incl,category_id,receipt_path,notes) VALUES(?,?,?,?,?,?,?,?)",
            (self.ex_date.get(), self.ex_supplier.get(), float(self.ex_excl.get() or 0), float(self.ex_vat.get() or 0), float(self.ex_incl.get() or 0), cat_id, self.ex_receipt.get(), self.ex_notes.get()),
        )
        self.refresh_expenses()

    def refresh_settings(self):
        row = self.db.q("SELECT * FROM settings WHERE id=1").fetchone()
        mapping = [(self.s_name, "company_name"), (self.s_email, "company_email"), (self.s_iban, "company_iban"), (self.s_kvk, "company_kvk"), (self.s_vat, "vat_rate"), (self.s_google, "google_client_path")]
        for e, k in mapping:
            e.delete(0, tk.END)
            e.insert(0, str(row[k] or ""))
        self.google_label.config(text=f"Google status: {'gekoppeld (voorbereid)' if row['google_connected'] else 'niet gekoppeld'}")

    def refresh_customers(self):
        rows = self.db.q("SELECT id,name,email,phone,city FROM customers ORDER BY name").fetchall()
        self.fill(self.customer_tree, rows)
        vals = [f"{r['id']} - {r['name']}" for r in rows]
        self.a_customer["values"] = vals
        self.i_customer["values"] = vals

    def refresh_agenda(self):
        rows = self.db.q("SELECT a.id,c.name customer,a.title,a.start_at,a.hours,a.hourly_rate,a.invoiced FROM appointments a JOIN customers c ON c.id=a.customer_id ORDER BY a.start_at DESC").fetchall()
        self.fill(self.agenda_tree, rows)
        self.i_appt_list.delete(0, tk.END)
        for r in rows:
            if not r["invoiced"]:
                self.i_appt_list.insert(tk.END, f"{r['id']} | {r['customer']} | {r['title']} | {r['hours']}u x {r['hourly_rate']}")

    def refresh_invoices(self):
        rows = self.db.q("SELECT i.id,i.invoice_no,c.name customer,i.issue_date,i.due_date,i.total,i.status FROM invoices i JOIN customers c ON c.id=i.customer_id ORDER BY i.id DESC").fetchall()
        self.fill(self.inv_tree, rows)
        inv_vals = [f"{r['id']} - {r['invoice_no']}" for r in rows]
        self.in_invoice["values"] = inv_vals

    def refresh_income(self):
        rows = self.db.q("SELECT inc.id,inc.date,inc.amount,inc.reference,COALESCE(i.invoice_no,''),inc.matched FROM incomes inc LEFT JOIN invoices i ON i.id=inc.invoice_id ORDER BY inc.date DESC").fetchall()
        self.fill(self.in_tree, rows)

    def refresh_expenses(self):
        cats = self.db.q("SELECT name FROM expense_categories ORDER BY name").fetchall()
        self.ex_cat["values"] = [c["name"] for c in cats]
        rows = self.db.q("SELECT e.id,e.date,e.supplier,e.amount_incl,COALESCE(c.name,''),e.receipt_path FROM expenses e LEFT JOIN expense_categories c ON c.id=e.category_id ORDER BY e.date DESC").fetchall()
        self.fill(self.ex_tree, rows)

    def refresh_report(self):
        income = self.db.q("SELECT COALESCE(SUM(amount),0) s FROM incomes").fetchone()["s"]
        expense = self.db.q("SELECT COALESCE(SUM(amount_incl),0) s FROM expenses").fetchone()["s"]
        unpaid = self.db.q("SELECT COALESCE(SUM(total),0) s FROM invoices WHERE status NOT IN ('betaald')").fetchone()["s"]
        paid = self.db.q("SELECT COALESCE(SUM(total),0) s FROM invoices WHERE status='betaald'").fetchone()["s"]
        text = (
            f"Omzet ontvangen: EUR {income:.2f}\n"
            f"Uitgaven: EUR {expense:.2f}\n"
            f"Resultaat: EUR {income - expense:.2f}\n"
            f"Facturen betaald: EUR {paid:.2f}\n"
            f"Facturen openstaand: EUR {unpaid:.2f}\n\n"
            "Tip: gebruik 'Auto-match op factuurnummer' in Inkomsten om bankregels te koppelen.\n"
            "Google Calendar koppeling staat voorbereid in Instellingen (OAuth client pad).\n"
        )
        self.report.delete("1.0", tk.END)
        self.report.insert(tk.END, text)

    def fill(self, tree, rows):
        for i in tree.get_children():
            tree.delete(i)
        for r in rows:
            tree.insert("", tk.END, values=tuple(r))

    def refresh_all(self):
        self.refresh_settings()
        self.refresh_customers()
        self.refresh_agenda()
        self.refresh_invoices()
        self.refresh_income()
        self.refresh_expenses()
        self.refresh_report()


if __name__ == "__main__":
    App().mainloop()
