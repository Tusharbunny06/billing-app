import streamlit as st
from datetime import date
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile

# --------------------------------
# Page Config
# --------------------------------
st.set_page_config(page_title="Professional Billing App", layout="centered")
st.title("🧾 Professional Billing Application")

# --------------------------------
# Company Details
# --------------------------------
st.subheader("🏢 Company Details")
company_name = st.text_input("Company Name", "ABC Traders")
company_address = st.text_area("Company Address", "Mumbai, India")
company_phone = st.text_input("Phone", "+91 98765 43210")

st.divider()

# --------------------------------
# Customer Details
# --------------------------------
st.subheader("👤 Customer Details")
customer_name = st.text_input("Customer Name")
bill_date = st.date_input("Bill Date", value=date.today())

st.divider()

# --------------------------------
# Session State
# --------------------------------
if "items" not in st.session_state:
    st.session_state["items"] = []

# --------------------------------
# Add Items
# --------------------------------
st.subheader("➕ Add Items")

with st.form("item_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        item = st.text_input("Item Name")
    with col2:
        qty = st.number_input("Quantity", min_value=1, step=1)
    with col3:
        price = st.number_input("Price / Unit", min_value=0.0, step=1.0)

    add_btn = st.form_submit_button("➕ Add Item")

    if add_btn and item.strip():
        st.session_state["items"].append([item, qty, price, qty * price])

# --------------------------------
# Bill Table
# --------------------------------
if st.session_state["items"]:
    df = pd.DataFrame(
        st.session_state["items"],
        columns=["Item", "Qty", "Price", "Total"]
    )

    st.subheader("📋 Invoice Items")
    st.dataframe(df, use_container_width=True)

    total_qty = df["Qty"].sum()
    grand_total = df["Total"].sum()

    st.markdown(f"### 🧮 Total Quantity: **{total_qty}**")
    st.markdown(f"### 💰 Grand Total: **₹{grand_total}**")

    # --------------------------------
    # PDF Generator with Multi-page Support
    # --------------------------------
    def generate_invoice_pdf():
        file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(file.name, pagesize=A4)
        width, height = A4

        def draw_header(y_pos):
            c.setFont("Helvetica-Bold", 20)
            c.drawString(2 * cm, height - 2 * cm, company_name)
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, height - 2.7 * cm, company_address)
            c.drawString(2 * cm, height - 3.3 * cm, f"Phone: {company_phone}")
            c.setFont("Helvetica-Bold", 16)
            c.drawRightString(width - 2 * cm, height - 2 * cm, "INVOICE")
            y = y_pos
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y, "Bill To:")
            c.setFont("Helvetica", 11)
            c.drawString(2 * cm, y - 15, customer_name)
            c.drawString(2 * cm, y - 30, f"Date: {bill_date}")
            return y - 70

        def draw_table_header(y_pos):
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y_pos, "Item")
            c.drawString(10 * cm, y_pos, "Qty")
            c.drawString(12 * cm, y_pos, "Price")
            c.drawString(15 * cm, y_pos, "Total")
            c.line(2 * cm, y_pos - 5, width - 2 * cm, y_pos - 5)
            return y_pos - 25

        y = draw_header(height - 5 * cm)
        y = draw_table_header(y)

        c.setFont("Helvetica", 11)
        for _, row in df.iterrows():
            if y < 3 * cm:  # If near bottom, create new page
                c.showPage()
                y = draw_header(height - 5 * cm)
                y = draw_table_header(y)
                c.setFont("Helvetica", 11)
            c.drawString(2 * cm, y, str(row["Item"]))
            c.drawString(10 * cm, y, str(row["Qty"]))
            c.drawString(12 * cm, y, f"₹{row['Price']}")
            c.drawString(15 * cm, y, f"₹{row['Total']}")
            y -= 20

        # Totals
        if y < 4 * cm:
            c.showPage()
            y = height - 5 * cm
        y -= 20
        c.line(10 * cm, y, width - 2 * cm, y)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(10 * cm, y - 20, "Grand Total:")
        c.drawRightString(width - 2 * cm, y - 20, f"₹{grand_total}")

        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(width / 2, 2 * cm, "Thank you for your business!")

        c.save()
        return file.name

    pdf_path = generate_invoice_pdf()

    with open(pdf_path, "rb") as f:
        st.download_button(
            "📥 Download Professional Invoice (PDF)",
            f,
            file_name="invoice.pdf",
            mime="application/pdf"
        )

    if st.button("🗑️ Clear Bill"):
        st.session_state["items"] = []
        st.rerun()

else:
    st.info("Add items to generate professional invoice")
