import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import webbrowser
from urllib.parse import quote

DB_PATH = "admin_data.db"


class DB:
    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id=1),
                company_name TEXT,
                company_email TEXT,
                google_client_path TEXT,
                google_connected INTEGER DEFAULT 0
            );

            INSERT OR IGNORE INTO settings (id, company_name, company_email, google_client_path, google_connected)
            VALUES (1, '', '', '', 0);

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                title TEXT NOT NULL,
                start_at TEXT,
                hours REAL DEFAULT 1,
                hourly_rate REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );

            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE,
                customer_id INTEGER,
                appointment_id INTEGER,
                description TEXT,
                amount REAL DEFAULT 0,
                status TEXT DEFAULT 'concept',
                scheduled_send_at TEXT,
                created_at TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(appointment_id) REFERENCES appointments(id)
            );

            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                reference TEXT,
                invoice_id INTEGER,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                category TEXT,
                receipt_path TEXT,
                notes TEXT
            );
            """
        )
        self.conn.commit()

    def q(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.title("Administratie Software (Windows MVP)")
        self.geometry("1100x700")

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True)

        self.settings_tab = ttk.Frame(tabs)
        self.customers_tab = ttk.Frame(tabs)
        self.appointments_tab = ttk.Frame(tabs)
        self.invoices_tab = ttk.Frame(tabs)
        self.income_tab = ttk.Frame(tabs)
        self.expense_tab = ttk.Frame(tabs)
        self.reports_tab = ttk.Frame(tabs)

        tabs.add(self.settings_tab, text="Instellingen")
        tabs.add(self.customers_tab, text="Klanten")
        tabs.add(self.appointments_tab, text="Afspraken")
        tabs.add(self.invoices_tab, text="Facturen")
        tabs.add(self.income_tab, text="Inkomsten")
        tabs.add(self.expense_tab, text="Uitgaven")
        tabs.add(self.reports_tab, text="Rapportage")

        self.build_settings_tab()
        self.build_customers_tab()
        self.build_appointments_tab()
        self.build_invoices_tab()
        self.build_income_tab()
        self.build_expense_tab()
        self.build_reports_tab()

        self.refresh_all()

    def labelled_entry(self, parent, label, row, default=""):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=4)
        entry = ttk.Entry(parent, width=50)
        entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="w", padx=5, pady=4)
        return entry

    def build_settings_tab(self):
        frm = ttk.Frame(self.settings_tab, padding=10)
        frm.pack(fill="x")
        self.company_name = self.labelled_entry(frm, "Bedrijfsnaam", 0)
        self.company_email = self.labelled_entry(frm, "Bedrijf e-mail", 1)
        self.google_client_path = self.labelled_entry(frm, "Google client secret pad", 2)

        def pick_file():
            p = filedialog.askopenfilename(title="Kies Google client secret JSON")
            if p:
                self.google_client_path.delete(0, tk.END)
                self.google_client_path.insert(0, p)

        ttk.Button(frm, text="Bladeren", command=pick_file).grid(row=2, column=2, padx=5)
        self.google_status = ttk.Label(frm, text="Google status: niet gekoppeld")
        self.google_status.grid(row=3, column=1, sticky="w", padx=5, pady=4)
        ttk.Button(frm, text="Opslaan instellingen", command=self.save_settings).grid(row=4, column=1, sticky="w", padx=5, pady=8)

    def save_settings(self):
        self.db.q(
            "UPDATE settings SET company_name=?, company_email=?, google_client_path=?, google_connected=? WHERE id=1",
            (self.company_name.get(), self.company_email.get(), self.google_client_path.get(), 1 if self.google_client_path.get() else 0),
        )
        self.load_settings()
        messagebox.showinfo("Opgeslagen", "Instellingen zijn opgeslagen.")

    def load_settings(self):
        row = self.db.q("SELECT * FROM settings WHERE id=1").fetchone()
        for w, key in [(self.company_name, "company_name"), (self.company_email, "company_email"), (self.google_client_path, "google_client_path")]:
            w.delete(0, tk.END)
            w.insert(0, row[key] or "")
        self.google_status.config(text=f"Google status: {'gekoppeld (basis)' if row['google_connected'] else 'niet gekoppeld'}")

    def build_customers_tab(self):
        frm = ttk.Frame(self.customers_tab, padding=10)
        frm.pack(fill="both", expand=True)
        self.c_name = self.labelled_entry(frm, "Naam", 0)
        self.c_email = self.labelled_entry(frm, "E-mail", 1)
        self.c_phone = self.labelled_entry(frm, "Telefoon", 2)
        self.c_address = self.labelled_entry(frm, "Adres", 3)
        ttk.Button(frm, text="Klant toevoegen", command=self.add_customer).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.customers_tree = ttk.Treeview(frm, columns=("id", "name", "email", "phone"), show="headings", height=15)
        for c in ("id", "name", "email", "phone"):
            self.customers_tree.heading(c, text=c)
        self.customers_tree.grid(row=5, column=0, columnspan=3, sticky="nsew")

    def add_customer(self):
        self.db.q("INSERT INTO customers (name,email,phone,address) VALUES (?,?,?,?)", (self.c_name.get(), self.c_email.get(), self.c_phone.get(), self.c_address.get()))
        self.refresh_customers()

    def build_appointments_tab(self):
        frm = ttk.Frame(self.appointments_tab, padding=10)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Klant").grid(row=0, column=0, sticky="w")
        self.appt_customer = ttk.Combobox(frm, width=47, state="readonly")
        self.appt_customer.grid(row=0, column=1, sticky="w")
        self.appt_title = self.labelled_entry(frm, "Titel", 1)
        self.appt_start = self.labelled_entry(frm, "Start (YYYY-MM-DD HH:MM)", 2)
        self.appt_hours = self.labelled_entry(frm, "Uren", 3, "1")
        self.appt_rate = self.labelled_entry(frm, "Uurtarief", 4, "75")
        ttk.Button(frm, text="Afspraak toevoegen", command=self.add_appointment).grid(row=5, column=1, sticky="w", pady=5)
        self.appt_tree = ttk.Treeview(frm, columns=("id", "customer", "title", "start", "hours", "rate"), show="headings", height=15)
        for c in ("id", "customer", "title", "start", "hours", "rate"):
            self.appt_tree.heading(c, text=c)
        self.appt_tree.grid(row=6, column=0, columnspan=3, sticky="nsew")

    def add_appointment(self):
        if not self.appt_customer.get():
            return
        cid = int(self.appt_customer.get().split(" - ")[0])
        self.db.q("INSERT INTO appointments (customer_id,title,start_at,hours,hourly_rate) VALUES (?,?,?,?,?)", (cid, self.appt_title.get(), self.appt_start.get(), float(self.appt_hours.get() or 0), float(self.appt_rate.get() or 0)))
        self.refresh_appointments()

    def build_invoices_tab(self):
        frm = ttk.Frame(self.invoices_tab, padding=10)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Afspraak").grid(row=0, column=0, sticky="w")
        self.inv_appt = ttk.Combobox(frm, width=70, state="readonly")
        self.inv_appt.grid(row=0, column=1, sticky="w")
        ttk.Button(frm, text="Factuur maken uit afspraak", command=self.create_invoice_from_appointment).grid(row=1, column=1, sticky="w", pady=5)

        self.inv_tree = ttk.Treeview(frm, columns=("id", "invoice_no", "customer", "amount", "status", "scheduled"), show="headings", height=14)
        for c in ("id", "invoice_no", "customer", "amount", "status", "scheduled"):
            self.inv_tree.heading(c, text=c)
        self.inv_tree.grid(row=2, column=0, columnspan=4, sticky="nsew")

        ttk.Button(frm, text="Status: bevestigd", command=lambda: self.set_invoice_status("bevestigd")).grid(row=3, column=0, pady=5)
        ttk.Button(frm, text="Verstuur via E-mail", command=self.send_invoice_email).grid(row=3, column=1)
        ttk.Button(frm, text="Verstuur via WhatsApp", command=self.send_invoice_whatsapp).grid(row=3, column=2)

    def create_invoice_from_appointment(self):
        if not self.inv_appt.get():
            return
        appt_id = int(self.inv_appt.get().split(" - ")[0])
        appt = self.db.q("SELECT a.*, c.name customer_name, c.id cid FROM appointments a JOIN customers c ON c.id=a.customer_id WHERE a.id=?", (appt_id,)).fetchone()
        amount = round((appt["hours"] or 0) * (appt["hourly_rate"] or 0), 2)
        inv_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{appt_id:04d}"
        desc = f"{appt['title']} ({appt['hours']}u x {appt['hourly_rate']})"
        self.db.q("INSERT INTO invoices (invoice_no,customer_id,appointment_id,description,amount,status,created_at) VALUES (?,?,?,?,?,?,?)", (inv_no, appt["cid"], appt_id, desc, amount, "concept", datetime.now().isoformat(timespec="minutes")))
        self.refresh_invoices()

    def selected_invoice(self):
        sel = self.inv_tree.selection()
        if not sel:
            return None
        return int(self.inv_tree.item(sel[0], "values")[0])

    def set_invoice_status(self, status):
        iid = self.selected_invoice()
        if not iid:
            return
        self.db.q("UPDATE invoices SET status=? WHERE id=?", (status, iid))
        self.refresh_invoices()

    def send_invoice_email(self):
        iid = self.selected_invoice()
        if not iid:
            return
        inv = self.db.q("SELECT i.invoice_no, i.amount, c.email, c.name FROM invoices i JOIN customers c ON c.id=i.customer_id WHERE i.id=?", (iid,)).fetchone()
        subject = quote(f"Factuur {inv['invoice_no']}")
        body = quote(f"Beste {inv['name']},\n\nHierbij factuur {inv['invoice_no']} van EUR {inv['amount']:.2f}.\n")
        webbrowser.open(f"mailto:{inv['email']}?subject={subject}&body={body}")
        self.db.q("UPDATE invoices SET status='verzonden' WHERE id=?", (iid,))
        self.refresh_invoices()

    def send_invoice_whatsapp(self):
        iid = self.selected_invoice()
        if not iid:
            return
        inv = self.db.q("SELECT i.invoice_no, i.amount, c.phone FROM invoices i JOIN customers c ON c.id=i.customer_id WHERE i.id=?", (iid,)).fetchone()
        phone = ''.join(ch for ch in (inv['phone'] or '') if ch.isdigit())
        txt = quote(f"Factuur {inv['invoice_no']} van EUR {inv['amount']:.2f}")
        webbrowser.open(f"https://wa.me/{phone}?text={txt}")
        self.db.q("UPDATE invoices SET status='verzonden' WHERE id=?", (iid,))
        self.refresh_invoices()

    def build_income_tab(self):
        frm = ttk.Frame(self.income_tab, padding=10)
        frm.pack(fill="both", expand=True)
        self.in_date = self.labelled_entry(frm, "Datum (YYYY-MM-DD)", 0, datetime.now().date().isoformat())
        self.in_amount = self.labelled_entry(frm, "Bedrag", 1)
        self.in_ref = self.labelled_entry(frm, "Referentie", 2)
        ttk.Label(frm, text="Factuur koppelen").grid(row=3, column=0, sticky="w")
        self.in_invoice = ttk.Combobox(frm, width=50, state="readonly")
        self.in_invoice.grid(row=3, column=1, sticky="w")
        ttk.Button(frm, text="Inkomst toevoegen", command=self.add_income).grid(row=4, column=1, sticky="w")
        self.in_tree = ttk.Treeview(frm, columns=("id", "date", "amount", "reference", "invoice"), show="headings", height=16)
        for c in ("id", "date", "amount", "reference", "invoice"):
            self.in_tree.heading(c, text=c)
        self.in_tree.grid(row=5, column=0, columnspan=3, sticky="nsew")

    def add_income(self):
        inv_id = int(self.in_invoice.get().split(" - ")[0]) if self.in_invoice.get() else None
        self.db.q("INSERT INTO incomes (date,amount,reference,invoice_id) VALUES (?,?,?,?)", (self.in_date.get(), float(self.in_amount.get() or 0), self.in_ref.get(), inv_id))
        self.refresh_income()

    def build_expense_tab(self):
        frm = ttk.Frame(self.expense_tab, padding=10)
        frm.pack(fill="both", expand=True)
        self.ex_date = self.labelled_entry(frm, "Datum (YYYY-MM-DD)", 0, datetime.now().date().isoformat())
        self.ex_amount = self.labelled_entry(frm, "Bedrag", 1)
        self.ex_cat = self.labelled_entry(frm, "Categorie", 2)
        self.ex_receipt = self.labelled_entry(frm, "Bon pad", 3)
        self.ex_notes = self.labelled_entry(frm, "Notities", 4)
        ttk.Button(frm, text="Kies bon", command=lambda: self.pick_receipt()).grid(row=3, column=2)
        ttk.Button(frm, text="Uitgave toevoegen", command=self.add_expense).grid(row=5, column=1, sticky="w")
        self.ex_tree = ttk.Treeview(frm, columns=("id", "date", "amount", "category", "receipt"), show="headings", height=16)
        for c in ("id", "date", "amount", "category", "receipt"):
            self.ex_tree.heading(c, text=c)
        self.ex_tree.grid(row=6, column=0, columnspan=3, sticky="nsew")

    def pick_receipt(self):
        p = filedialog.askopenfilename(title="Kies bonbestand")
        if p:
            self.ex_receipt.delete(0, tk.END)
            self.ex_receipt.insert(0, p)

    def add_expense(self):
        self.db.q("INSERT INTO expenses (date,amount,category,receipt_path,notes) VALUES (?,?,?,?,?)", (self.ex_date.get(), float(self.ex_amount.get() or 0), self.ex_cat.get(), self.ex_receipt.get(), self.ex_notes.get()))
        self.refresh_expenses()

    def build_reports_tab(self):
        frm = ttk.Frame(self.reports_tab, padding=10)
        frm.pack(fill="both", expand=True)
        self.report_text = tk.Text(frm, height=25)
        self.report_text.pack(fill="both", expand=True)
        ttk.Button(frm, text="Ververs rapport", command=self.refresh_report).pack(pady=5)

    def refresh_customers(self):
        self.fill_tree(self.customers_tree, self.db.q("SELECT id,name,email,phone FROM customers ORDER BY id DESC").fetchall())
        customers = self.db.q("SELECT id,name FROM customers ORDER BY name").fetchall()
        vals = [f"{r['id']} - {r['name']}" for r in customers]
        self.appt_customer["values"] = vals

    def refresh_appointments(self):
        rows = self.db.q("SELECT a.id, c.name customer, a.title, a.start_at, a.hours, a.hourly_rate rate FROM appointments a LEFT JOIN customers c ON c.id=a.customer_id ORDER BY a.id DESC").fetchall()
        self.fill_tree(self.appt_tree, rows)
        self.inv_appt["values"] = [f"{r['id']} - {r['customer']} - {r['title']}" for r in rows]

    def refresh_invoices(self):
        rows = self.db.q("SELECT i.id, i.invoice_no, c.name customer, i.amount, i.status, COALESCE(i.scheduled_send_at,'') scheduled FROM invoices i LEFT JOIN customers c ON c.id=i.customer_id ORDER BY i.id DESC").fetchall()
        self.fill_tree(self.inv_tree, rows)
        invs = self.db.q("SELECT id, invoice_no FROM invoices ORDER BY id DESC").fetchall()
        self.in_invoice["values"] = [f"{r['id']} - {r['invoice_no']}" for r in invs]

    def refresh_income(self):
        rows = self.db.q("SELECT inc.id, inc.date, inc.amount, inc.reference, COALESCE(i.invoice_no,'') invoice FROM incomes inc LEFT JOIN invoices i ON i.id=inc.invoice_id ORDER BY inc.id DESC").fetchall()
        self.fill_tree(self.in_tree, rows)

    def refresh_expenses(self):
        rows = self.db.q("SELECT id,date,amount,category,receipt_path FROM expenses ORDER BY id DESC").fetchall()
        self.fill_tree(self.ex_tree, rows)

    def refresh_report(self):
        income = self.db.q("SELECT COALESCE(SUM(amount),0) s FROM incomes").fetchone()["s"]
        expense = self.db.q("SELECT COALESCE(SUM(amount),0) s FROM expenses").fetchone()["s"]
        balance = income - expense
        txt = (
            f"Inkomsten totaal: EUR {income:.2f}\n"
            f"Uitgaven totaal: EUR {expense:.2f}\n"
            f"Saldo: EUR {balance:.2f}\n\n"
            "Facturen per status:\n"
        )
        for r in self.db.q("SELECT status, COUNT(*) c, COALESCE(SUM(amount),0) amt FROM invoices GROUP BY status").fetchall():
            txt += f"- {r['status']}: {r['c']} facturen (EUR {r['amt']:.2f})\n"
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, txt)

    def fill_tree(self, tree, rows):
        for i in tree.get_children():
            tree.delete(i)
        for r in rows:
            tree.insert("", tk.END, values=tuple(r))

    def refresh_all(self):
        self.load_settings()
        self.refresh_customers()
        self.refresh_appointments()
        self.refresh_invoices()
        self.refresh_income()
        self.refresh_expenses()
        self.refresh_report()


if __name__ == "__main__":
    App().mainloop()
