import sqlite3
from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="FactoryFlow | Order & Dispatch", page_icon="🏭", layout="wide")
DB_PATH = "factoryflow.db"

STATUSES = ["New", "In Production", "Sent for Polishing", "Polishing Returned", "Ready to Dispatch", "Partially Dispatched", "Dispatched", "On Hold", "Returned", "Cancelled"]

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT NOT NULL,
            customer TEXT NOT NULL,
            channel TEXT DEFAULT 'Phone',
            product TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            rate REAL,
            status TEXT NOT NULL DEFAULT 'New',
            due_date TEXT,
            payment_hold INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            event_date TEXT NOT NULL,
            event_type TEXT NOT NULL,
            quantity REAL,
            notes TEXT DEFAULT '',
            actor TEXT DEFAULT '',
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS polish_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            vendor TEXT NOT NULL,
            sent_kg REAL NOT NULL,
            returned_pieces REAL DEFAULT 0,
            returned_kg REAL,
            sent_date TEXT NOT NULL,
            return_date TEXT,
            notes TEXT DEFAULT '',
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )""")
        count = con.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"]
        if count == 0:
            seed = [
                ("2026-09-01","Gupta Traders Ambala","Phone","Kadai No.10",200,"pcs",185,"Dispatched",None,0,"Sample from assignment; duplicate-like row should be verified"),
                ("2026-09-01","Sharma Bartan Bhandar Karnal","WhatsApp","Patila set 5pc",40,"set",920,"Dispatched",None,0,""),
                ("2026-09-01","Gupta Traders Ambala","WhatsApp","Kadai No.10",200,"pcs",185,"On Hold",None,0,"Possible duplicate from order sheet; verify before merging"),
                ("2026-09-02","New Delhi Steel House","Phone","Thali 12 inch",50,"dozen",610,"Dispatched",None,0,""),
                ("2026-09-02","Jain Crockery Panipat","WhatsApp","Kadhai No 10",150,"pcs",192,"New",None,0,"Repeated WhatsApp order; verify if duplicate"),
                ("2026-09-02","Online - Kunal","Online","Dinner set 24pc",12,"set",2350,"Dispatched",None,0,"Amazon"),
                ("2026-09-03","Sharma Bartan Bhandar Karnal","Phone","Gilas 300ml",30,"dozen",260,"On Hold",None,1,"Old dues noted as ₹1.8 lakh"),
                ("2026-09-03","Bansal & Sons Rohtak","WhatsApp","Tope No.6",120,"pcs",340,"Sent for Polishing",None,0,"Awaiting polishing return"),
                ("2026-09-03","Unconfirmed customer","Phone","Thali 12 inch",20,"dozen",600,"Dispatched",None,0,"Customer name missing in source sheet; verify"),
                ("2026-09-04","Gupta Traders Ambala","Phone","Patila set 5pc",25,"set",950,"Dispatched",None,0,""),
                ("2026-09-04","Jain Crockery Panipat","WhatsApp","Kadhai No 10",150,"pcs",192,"New",None,0,"Repeated row; confirm whether a new order"),
                ("2026-09-04","Mehra Kitchenware Jalandhar","Phone","Kadai No.10",300,"pcs",180,"Partially Dispatched",None,0,"180 dispatched; 120 remaining"),
                ("2026-09-04","New Delhi Steel House","Phone","Bhagona 8L",60,"pcs",410,"Sent for Polishing",None,0,""),
                ("2026-09-05","Online - Kunal","Online","Kadai No.10",35,"pcs",240,"Dispatched",None,0,"Flipkart"),
                ("2026-09-05","Bansal & Sons Rohtak","WhatsApp","Tope No.6",120,"pcs",340,"Sent for Polishing",None,0,"Repeated pending row in source; verify duplicate"),
                ("2026-09-05","Sharma Bartan Bhandar Karnal","Phone","Gilas 300ml",-6,"dozen",260,"Returned",None,0,"Return due to dents; negative quantity retained from source"),
                ("2026-09-05","Verma Utensils Sonipat","Phone","Thali 12 inch",40,"dozen",605,"Dispatched",None,0,""),
                ("2026-09-06","Mehra Kitchenware Jalandhar","Phone","Kadai No.10",120,"pcs",180,"Dispatched",None,0,"Remaining 120 dispatched"),
                ("2026-09-06","Gupta Traders Ambala","Phone","Bhagona 8 ltr",40,"pcs",400,"Sent for Polishing",None,0,""),
                ("2026-09-06","Jain Crockery Panipat","WhatsApp","Gilas 300 ml",25,"dozen",255,"Dispatched",None,0,""),
                ("2026-09-06","Verma Utensils Sonipat","Phone","Kadhai 10 no.",180,"kg",None,"On Hold",None,0,"Rate confirmation required"),
                ("2026-09-07","New Delhi Steel House","Phone","Thali 12 inch",50,"dozen",610,"Dispatched",None,0,""),
                ("2026-09-07","Online - Kunal","Online","Patila set 5pc",8,"set",1199,"Dispatched",None,0,"Amazon"),
                ("2026-09-07","Sharma Bartan Bhandar Karnal","Phone","Patila set 5pc",20,"set",920,"On Hold",None,1,"Payment hold"),
                ("2026-09-07","Bansal & Sons Rohtak","WhatsApp","Tope No.6",60,"pcs",340,"New",None,0,"New order")
            ]
            for row in seed:
                con.execute("""INSERT INTO orders(order_date,customer,channel,product,quantity,unit,rate,status,due_date,payment_hold,notes,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (*row, datetime.now().isoformat(timespec="seconds")))
        con.commit()

def fetch_orders():
    with db() as con:
        return pd.read_sql_query("SELECT * FROM orders ORDER BY order_date DESC, id DESC", con)

def money(v):
    try:
        return f"₹{float(v):,.0f}"
    except (TypeError, ValueError):
        return "—"

init_db()
st.title("🏭 FactoryFlow")
st.caption("A lightweight order-to-dispatch tracker for small manufacturing teams")
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Orders", "Polishing & Material", "Dispatch / Updates", "Reports", "Settings"])
    st.divider()
    st.caption("Demo data is based on the fictional Vardhan Steelware assignment. Verify ambiguous rows before treating them as real records.")

orders = fetch_orders()

if page == "Dashboard":
    st.subheader("Morning overview")
    total = len(orders)
    active = int((~orders.status.isin(["Dispatched", "Cancelled", "Returned"])).sum())
    delayed_or_stuck = int(orders.status.isin(["On Hold", "Sent for Polishing", "Partially Dispatched"]).sum())
    payment_holds = int(orders.payment_hold.fillna(0).astype(int).sum())
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Orders in register", total)
    c2.metric("Active orders", active)
    c3.metric("Stuck / partial", delayed_or_stuck)
    c4.metric("Payment holds", payment_holds)
    st.markdown("### Where orders are stuck")
    status_counts = orders.groupby("status", dropna=False).size().reset_index(name="Orders").sort_values("Orders", ascending=False)
    st.bar_chart(status_counts.set_index("status"))
    left,right = st.columns(2)
    with left:
        st.markdown("### Orders needing attention")
        attention = orders[orders.status.isin(["On Hold","Sent for Polishing","Partially Dispatched"]) | orders.rate.isna()]
        show = attention[["id","customer","product","quantity","unit","status","payment_hold","notes"]].copy()
        show["payment_hold"] = show["payment_hold"].map({1:"Yes",0:"No"})
        st.dataframe(show, use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Recent updates")
        with db() as con:
            ev = pd.read_sql_query("""SELECT e.event_date, o.customer, o.product, e.event_type, e.quantity, e.actor, e.notes
                FROM events e JOIN orders o ON o.id=e.order_id ORDER BY e.id DESC LIMIT 10""", con)
        if ev.empty:
            st.info("No updates recorded yet. Add an order update from Dispatch / Updates.")
        else:
            st.dataframe(ev, use_container_width=True, hide_index=True)

elif page == "Orders":
    st.subheader("Order register")
    with st.expander("➕ Create a new order", expanded=False):
        with st.form("new_order", clear_on_submit=True):
            a,b,c = st.columns(3)
            order_date = a.date_input("Order date", value=date.today())
            customer = b.text_input("Customer / distributor", placeholder="e.g., Gupta Traders Ambala")
            channel = c.selectbox("Order channel", ["Phone","WhatsApp","Walk-in","Online","Other"])
            d,e,f = st.columns(3)
            product = d.text_input("Product", placeholder="e.g., Kadai No.10")
            quantity = e.number_input("Quantity", min_value=0.0, value=1.0, step=1.0)
            unit = f.selectbox("Unit", ["pcs","dozen","set","kg","box","other"])
            g,h,i = st.columns(3)
            rate = g.number_input("Rate (₹ per unit)", min_value=0.0, value=0.0, step=10.0)
            due = h.date_input("Expected delivery date", value=date.today())
            status = i.selectbox("Initial status", ["New","In Production","On Hold"])
            notes = st.text_area("Notes / special instructions")
            submitted = st.form_submit_button("Save order", type="primary")
            if submitted:
                if not customer.strip() or not product.strip():
                    st.error("Customer and product are required.")
                else:
                    with db() as con:
                        con.execute("""INSERT INTO orders(order_date,customer,channel,product,quantity,unit,rate,status,due_date,payment_hold,notes,created_at)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (order_date.isoformat(),customer.strip(),channel,product.strip(),quantity,unit,rate if rate > 0 else None,status,due.isoformat(),0,notes,datetime.now().isoformat(timespec="seconds")))
                        con.commit()
                    st.success("Order saved.")
                    st.rerun()
    search = st.text_input("Search by customer, product, status or note")
    statuses = st.multiselect("Filter status", STATUSES, default=[])
    view = orders.copy()
    if search:
        mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]
    if statuses:
        view = view[view.status.isin(statuses)]
    st.dataframe(view[["id","order_date","customer","channel","product","quantity","unit","rate","status","due_date","payment_hold","notes"]],
                 use_container_width=True, hide_index=True)
    st.caption("The source pack contains possible duplicates, missing customer names, mixed units, and an unconfirmed rate. These are intentionally flagged in demo notes rather than silently corrected.")
    st.markdown("### Update an order")
    if not orders.empty:
        selected = st.selectbox("Choose order ID", orders.id.tolist(), format_func=lambda x: f"#{x} — {orders.loc[orders.id==x,'customer'].iloc[0]} / {orders.loc[orders.id==x,'product'].iloc[0]}")
        current = orders[orders.id==selected].iloc[0]
        with st.form("edit_order"):
            x,y,z = st.columns(3)
            new_status = x.selectbox("Status", STATUSES, index=STATUSES.index(current.status) if current.status in STATUSES else 0)
            payment_hold = y.checkbox("Payment hold", value=bool(current.payment_hold))
            new_due = z.text_input("Due date (YYYY-MM-DD)", value="" if pd.isna(current.due_date) else str(current.due_date))
            new_notes = st.text_area("Notes", value="" if pd.isna(current.notes) else str(current.notes))
            if st.form_submit_button("Update order"):
                with db() as con:
                    con.execute("UPDATE orders SET status=?, payment_hold=?, due_date=?, notes=? WHERE id=?",
                                (new_status,int(payment_hold),new_due or None,new_notes,selected))
                    con.execute("INSERT INTO events(order_id,event_date,event_type,notes,actor) VALUES(?,?,?,?,?)",
                                (selected,date.today().isoformat(),f"Status changed to {new_status}",new_notes,"User"))
                    con.commit()
                st.success("Order updated.")
                st.rerun()

elif page == "Polishing & Material":
    st.subheader("External polishing and material reconciliation")
    st.write("Record each lot sent to an outside karigar and what comes back. Do not treat a difference as wastage until it is reviewed.")
    with st.form("polish_form", clear_on_submit=True):
        a,b,c = st.columns(3)
        if orders.empty:
            st.warning("Create an order first.")
            selected_order = None
        else:
            selected_order = a.selectbox("Related order", orders.id.tolist(), format_func=lambda x: f"#{x} — {orders.loc[orders.id==x,'customer'].iloc[0]} / {orders.loc[orders.id==x,'product'].iloc[0]}")
        vendor = b.text_input("Polishing vendor / karigar", placeholder="e.g., Pappu")
        sent_date = c.date_input("Sent date", value=date.today())
        d,e,f = st.columns(3)
        sent_kg = d.number_input("Weight sent (kg)", min_value=0.0, value=0.0, step=1.0)
        returned_kg = e.number_input("Weight returned (kg)", min_value=0.0, value=0.0, step=1.0)
        returned_pieces = f.number_input("Pieces returned", min_value=0.0, value=0.0, step=1.0)
        return_date = st.date_input("Return date", value=date.today())
        polish_notes = st.text_input("Notes")
        save_polish = st.form_submit_button("Save polishing lot", type="primary")
        if save_polish and selected_order is not None:
            if not vendor.strip() or sent_kg <= 0:
                st.error("Enter a vendor and a positive sent weight.")
            else:
                with db() as con:
                    con.execute("""INSERT INTO polish_batches(order_id,vendor,sent_kg,returned_pieces,returned_kg,sent_date,return_date,notes)
                        VALUES(?,?,?,?,?,?,?,?)""",(selected_order,vendor.strip(),sent_kg,returned_pieces,returned_kg,sent_date.isoformat(),return_date.isoformat(),polish_notes))
                    con.execute("INSERT INTO events(order_id,event_date,event_type,quantity,notes,actor) VALUES(?,?,?,?,?,?)",
                                (selected_order,date.today().isoformat(),"Polishing lot recorded",returned_pieces,polish_notes,vendor.strip()))
                    con.commit()
                st.success("Polishing lot saved.")
                st.rerun()
    with db() as con:
        polish = pd.read_sql_query("""SELECT p.id, p.sent_date, p.return_date, o.customer, o.product, p.vendor, p.sent_kg, p.returned_kg,
            (p.sent_kg-COALESCE(p.returned_kg,0)) AS kg_difference, p.returned_pieces, p.notes
            FROM polish_batches p JOIN orders o ON o.id=p.order_id ORDER BY p.id DESC""", con)
    st.markdown("### Polishing register")
    if polish.empty:
        st.info("No polishing lots recorded yet.")
    else:
        st.dataframe(polish, use_container_width=True, hide_index=True)
        st.markdown("### Reconciliation flags")
        flags = polish[polish.kg_difference.abs() > 0.01]
        if flags.empty:
            st.success("No weight differences in the recorded lots.")
        else:
            st.warning(f"{len(flags)} lot(s) have a non-zero weight difference and need review.")
            st.dataframe(flags[["id","customer","product","vendor","sent_kg","returned_kg","kg_difference"]], use_container_width=True, hide_index=True)

elif page == "Dispatch / Updates":
    st.subheader("Dispatch and order timeline")
    if orders.empty:
        st.info("Create an order first.")
    else:
        selected = st.selectbox("Order", orders.id.tolist(), format_func=lambda x: f"#{x} — {orders.loc[orders.id==x,'customer'].iloc[0]} / {orders.loc[orders.id==x,'product'].iloc[0]} ({orders.loc[orders.id==x,'status'].iloc[0]})")
        current = orders[orders.id==selected].iloc[0]
        st.info(f"Ordered quantity: {current.quantity:g} {current.unit} · Current status: {current.status}")
        with st.form("event_form", clear_on_submit=True):
            a,b,c = st.columns(3)
            event_date = a.date_input("Update date", value=date.today())
            event_type = b.selectbox("Update type", ["Production started","Sent for polishing","Polishing returned","Ready to dispatch","Dispatch","Partial dispatch","Return received","Payment hold applied","Payment hold released","Customer update","Other"])
            quantity = c.number_input("Quantity affected (if applicable)", min_value=0.0, value=0.0, step=1.0)
            actor = st.text_input("Updated by", placeholder="e.g., Ramesh")
            notes = st.text_area("What happened / reference")
            if st.form_submit_button("Add update", type="primary"):
                with db() as con:
                    con.execute("INSERT INTO events(order_id,event_date,event_type,quantity,notes,actor) VALUES(?,?,?,?,?,?)",
                                (selected,event_date.isoformat(),event_type,quantity if quantity > 0 else None,notes,actor))
                    status_map = {"Production started":"In Production","Sent for polishing":"Sent for Polishing","Polishing returned":"Polishing Returned","Ready to dispatch":"Ready to Dispatch","Dispatch":"Dispatched","Partial dispatch":"Partially Dispatched","Return received":"Returned","Payment hold applied":"On Hold","Payment hold released":"New"}
                    if event_type in status_map:
                        con.execute("UPDATE orders SET status=?, payment_hold=CASE WHEN ?='Payment hold applied' THEN 1 WHEN ?='Payment hold released' THEN 0 ELSE payment_hold END WHERE id=?",
                                    (status_map[event_type],event_type,event_type,selected))
                    con.commit()
                st.success("Update recorded.")
                st.rerun()
        with db() as con:
            timeline = pd.read_sql_query("SELECT event_date,event_type,quantity,actor,notes FROM events WHERE order_id=? ORDER BY id DESC",(con,selected))
        st.markdown("### Timeline")
        if timeline.empty:
            st.info("No timeline updates yet.")
        else:
            st.dataframe(timeline, use_container_width=True, hide_index=True)

elif page == "Reports":
    st.subheader("Morning reports")
    r1,r2,r3 = st.tabs(["Orders at risk","Dispatch backlog","Payment holds"])
    with r1:
        risk = orders[orders.status.isin(["On Hold","Sent for Polishing","Partially Dispatched"]) | orders.rate.isna()].copy()
        st.write("Orders that may need an owner decision or follow-up.")
        st.dataframe(risk[["id","customer","product","quantity","unit","rate","status","due_date","payment_hold","notes"]], use_container_width=True, hide_index=True)
        st.download_button("Download risk report CSV", risk.to_csv(index=False).encode("utf-8"), "orders_at_risk.csv", "text/csv")
    with r2:
        backlog = orders[~orders.status.isin(["Dispatched","Cancelled","Returned"])].copy()
        st.write(f"{len(backlog)} orders are not marked fully dispatched or closed.")
        st.dataframe(backlog[["id","order_date","customer","product","quantity","unit","status","due_date"]], use_container_width=True, hide_index=True)
        st.download_button("Download backlog CSV", backlog.to_csv(index=False).encode("utf-8"), "dispatch_backlog.csv", "text/csv")
    with r3:
        holds = orders[(orders.payment_hold.fillna(0).astype(int)==1) | (orders.status=="On Hold")].copy()
        st.write("Payment-related holds and all orders marked On Hold. Confirm reason before release.")
        st.dataframe(holds[["id","customer","product","quantity","unit","status","payment_hold","notes"]], use_container_width=True, hide_index=True)
        st.download_button("Download payment holds CSV", holds.to_csv(index=False).encode("utf-8"), "payment_holds.csv", "text/csv")
    st.download_button("Download full order register CSV", orders.to_csv(index=False).encode("utf-8"), "factoryflow_orders.csv", "text/csv")

elif page == "Settings":
    st.subheader("Data and demo settings")
    st.warning("This prototype stores data in a local SQLite database. It has no login, cloud sync, automatic backups, or production security controls.")
    st.write("Use the demo dataset to explore the workflow. The original client pack contains ambiguous duplicates and inconsistent status wording; the app preserves them with notes for verification.")
    if st.button("Export database backup"):
        with open(DB_PATH,"rb") as f:
            st.download_button("Download SQLite database", f.read(), "factoryflow_backup.db", "application/octet-stream")
    if st.button("Reset demo data", type="secondary"):
        with db() as con:
            con.execute("DELETE FROM events")
            con.execute("DELETE FROM polish_batches")
            con.execute("DELETE FROM orders")
            con.commit()
        st.info("Demo rows removed. Reload the page and create your own orders.")
        st.rerun()

st.divider()
st.caption("FactoryFlow prototype • Phase 1 focus: visibility, handoffs, partial dispatch, external polishing, and exceptions.")
