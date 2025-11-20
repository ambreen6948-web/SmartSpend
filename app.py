# app.py — SmartSpend (Pro student version)
import streamlit as st
import pandas as pd
import os, json
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from datetime import date

# ---------------------------
# Basic Page / App Config
# ---------------------------
st.set_page_config(page_title="SmartSpend", page_icon="💸", layout="wide")

# ---------------------------
# File paths (persistent storage)
# ---------------------------
EXP_FILE = "expenses.csv"
INC_FILE = "incomes.csv"
INV_FILE = "investments.csv"
GOAL_FILE = "goals.csv"
SET_FILE = "settings.json"

# ---------------------------
# Helper: init files if missing
# ---------------------------
def ensure_files():
    if not os.path.exists(EXP_FILE):
        pd.DataFrame(columns=["Date","Category","Description","Amount"]).to_csv(EXP_FILE, index=False)
    if not os.path.exists(INC_FILE):
        pd.DataFrame(columns=["Date","Source","Amount"]).to_csv(INC_FILE, index=False)
    if not os.path.exists(INV_FILE):
        pd.DataFrame(columns=["Date","Type","Amount","CurrentValue"]).to_csv(INV_FILE, index=False)
    if not os.path.exists(GOAL_FILE):
        pd.DataFrame(columns=["Name","TargetAmount","SavedSoFar","TargetDate"]).to_csv(GOAL_FILE, index=False)
    if not os.path.exists(SET_FILE):
        default = {"currency": "SAR", "monthly_budget": 0.0, "theme": "black-neon"}
        with open(SET_FILE, "w") as f:
            json.dump(default, f)
ensure_files()

# ---------------------------
# Load helpers
# ---------------------------
@st.cache_data
def load_csv(path): return pd.read_csv(path)
def save_csv(df, path): df.to_csv(path, index=False)
def load_settings():
    with open(SET_FILE, "r") as f: return json.load(f)
def save_settings(d):
    with open(SET_FILE, "w") as f: json.dump(d, f)

# ---------------------------
# Load data
# ---------------------------
df_exp = pd.read_csv(EXP_FILE)
df_inc = pd.read_csv(INC_FILE)
df_inv = pd.read_csv(INV_FILE)
df_goal = pd.read_csv(GOAL_FILE)
settings = load_settings()

# ---------------------------
# Normalize date columns (convert to datetime)
# ---------------------------
for df, col in [(df_exp,"Date"), (df_inc,"Date"), (df_inv,"Date"), (df_goal,"TargetDate")]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")  # invalid/missing become NaT

# ---------------------------
# Session state
# ---------------------------
if "currency" not in st.session_state: st.session_state.currency = settings.get("currency","SAR")
if "monthly_budget" not in st.session_state: st.session_state.monthly_budget = float(settings.get("monthly_budget",0.0))
if "page" not in st.session_state:
    st.session_state.page = "Landing"

# ---------------------------
# Sidebar Navigation (modern + professional)
# ---------------------------
if st.session_state.page not in ["Landing", "login"]:
    # Define menu items with icons
    menu_items = [
        ("Dashboard", "💹"),
        ("Add Expense", "💸"),
        ("Add Income", "💰"),
        ("Add Investment", "📈"),
        ("View Expenses", "📋"),
        ("Goals", "🎯"),
        ("Settings", "⚙️"),
        ("AI Coach", " 🤖")
    ]

    # Build display labels with icons
    menu_labels = [f"{icon} {name}" for name, icon in menu_items]

    # Find index of current page
    current_idx = next((i for i, (name, _) in enumerate(menu_items) if name == st.session_state.page), 0)

    # Sidebar title
    st.sidebar.markdown("<h2 style='text-align:center; color:#00fff7;'>📂 SmartSpend Menu</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Use radio buttons with icons
    choice_label = st.sidebar.radio(
        "Navigate",
        menu_labels,
        index=current_idx,
        label_visibility="collapsed"  # hide default label for cleaner look
    )

    # Map selected label back to page name
    selected_page = menu_items[menu_labels.index(choice_label)][0]

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

# ---------------------------
# CSS
# ---------------------------
def apply_css(page_name):
    bg = {
        "Landing": "https://img.freepik.com/premium-photo/beautiful-woman-portrait-exposure-city-effect-cityscape-reflection_916191-157179.jpg",
        "Dashboard": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "Add Expense": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "Add Income": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "Add Investment": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "View Expenses": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "Goals": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "Settings": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg",
        "AI Coach": "https://as1.ftcdn.net/v2/jpg/06/04/92/34/1000_F_604923462_ezo4yBKPS5flnaE91U9mZaFI8dKWryBd.jpg"
    }.get(page_name, "")
    gradient = "rgba(0,0,0,0.7)" if page_name=="Landing" else "rgba(0,0,0,0.7)"

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient({gradient},{gradient}), url('{bg}');
        background-size: cover; background-position: center;
    }}
    .neon {{
        color: #00fff7; text-align:center; font-family: 'Courier New', monospace;
        text-shadow: 0 0 5px #00fff7, 0 0 10px #00fff7, 0 0 20px #00fff7, 0 0 40px #00fff7;
    }}
    .neon-small {{
        color: #fff; text-align:center; font-family:'Courier New', monospace;
        text-shadow: 0 0 3px #00fff7, 0 0 6px #00fff7, 0 0 12px #00fff7;
    }}
    .stButton>button {{
        background-color:#00fff7; color:black; font-weight:bold;
        border-radius:10px; padding:10px 30px; font-size:18px;
        box-shadow:0 0 10px #00fff7; transition:0.3s;
    }}
    .stButton>button:hover {{
        box-shadow:0 0 20px #00fff7; transform: scale(1.05);
    }}
    .marquee {{
        width:100%; overflow:hidden; white-space:nowrap; box-sizing:border-box; margin-bottom:30px;
    }}
    .marquee span {{
        display:inline-block; padding-left:100%; animation:marquee 25s linear infinite;
        font-size:18px; color:#00fff7; font-family:'Courier New', monospace;
        text-shadow:0 0 5px #00fff7,0 0 10px #00fff7;
    }}
    @keyframes marquee {{ 0% {{transform:translateX(0%)}} 100% {{transform:translateX(-100%)}} }}
    </style>
    """, unsafe_allow_html=True)

apply_css(st.session_state.page)

# ---------------------------
# Utilities
# ---------------------------
def currency_format(amount): return f"{amount:,.2f} {st.session_state.currency}"
def compute_smartscore(total_income, total_expenses, total_investments, budget, goals_df):
    savings_rate = max(0.0, (total_income - total_expenses - total_investments)/total_income) if total_income>0 else 0
    budget_score = 1.0 if budget==0 else max(0.0, 1 - max(0, total_expenses-budget)/budget)
    goal_score = 0.5
    if len(goals_df)>0:
        prog = []
        for _, r in goals_df.iterrows():
            targ = float(r.get("TargetAmount",0) or 0)
            saved = float(r.get("SavedSoFar",0) or 0)
            prog.append(1.0 if targ<=0 else min(1.0, saved/targ))
        goal_score = sum(prog)/len(prog)
    return int(max(0,min(100, round(savings_rate*0.45 + budget_score*0.3 + goal_score*0.25)*100)))

# ---------------------------
# Page rendering
# ---------------------------
if st.session_state.page=="Landing":
    # Top-right buttons
    col1,col2,col3,col4 = st.columns([4,4,2,2])
    with col3:
        if st.button("🚀 Stay logged out"):
            st.session_state.page="dashboard"; st.rerun()
    with col4:
        if st.button("🔒 Login"):
            st.session_state.page="login"; st.rerun()
    
    # Hero
    st.markdown("<div style='text-align:center; margin-top:100px;'>"
                "<h1 class='neon'>💸 Welcome to SmartSpend</h1>"
                "<h3 class='neon-small'>Track expenses, manage your budget, and maximize your wealth effortlessly.</h3>"
                "</div>", unsafe_allow_html=True)
    st.markdown("---")
    # Marquee
    st.markdown("<div class='marquee'><span>🟢 Auto-categorization &nbsp;|&nbsp; 🟢 Dashboards & charts &nbsp;|&nbsp; 🟢 AI insights & coaching &nbsp;|&nbsp; 🟢 Track goals, savings & budget &nbsp;|&nbsp; 🟢 SmartSpend Score &nbsp;|&nbsp; 🟢 Professional & fun!</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='text-align:center;'>"
    "<h5 class='small-muted'>Built for students, employees, and hustlers. Design by Zafira Ambreen & Samreen. Tech by Streamlit.</h5>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.page=="login":
    apply_css("Landing")
    st.markdown("<div style='text-align:center; margin-top:150px;'>"
                "<h1 class='neon'>🔒 Login to SmartSpend</h1>"
                "<h3 class='neon-small'>Enter credentials to access your dashboard</h3>"
                "</div>", unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if username and password:
            st.session_state.page="home"
            st.success("Logged in successfully!"); st.rerun()
        else: st.error("Enter valid credentials")
    if st.button("⬅️ Back"):
        st.session_state.page="Landing"; st.rerun()

# ---------------------------
# Dashboard
# ---------------------------
if st.session_state.page == "Dashboard":
    apply_css("Dashboard")  # apply custom background & neon style
    st.title("💸 SmartSpend Dashboard")

    # --- reload CSVs fresh ---
    df_exp = pd.read_csv(EXP_FILE)
    df_inc = pd.read_csv(INC_FILE)
    df_inv = pd.read_csv(INV_FILE)
    df_goal = pd.read_csv(GOAL_FILE)

    # Ensure Date column is datetime type
    for d in [df_exp, df_inc, df_inv]:
        if not d.empty and "Date" in d.columns:
            d["Date"] = pd.to_datetime(d["Date"], errors="coerce")

    # ---------- CALCULATIONS ----------
    total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
    total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
    total_investments = df_inv["CurrentValue"].sum() if ("CurrentValue" in df_inv.columns and not df_inv.empty) else df_inv["Amount"].sum() if not df_inv.empty else 0.0
    total_savings = max(0.0, total_income - total_expenses - total_investments)

    now = datetime.now()
    this_month_exp = df_exp[(df_exp["Date"].dt.month == now.month) & (df_exp["Date"].dt.year == now.year)]["Amount"].sum() if (not df_exp.empty and df_exp["Date"].notna().all()) else 0.0
    budget = st.session_state.monthly_budget

    # ---------- SMARTSCORE & ESTIMATED FUTURE SAVINGS ----------
    def compute_smartscore(total_income, total_expenses, total_investments, budget, goals_df):
        savings_rate = max(0.0, (total_income - total_expenses - total_investments) / total_income) if total_income > 0 else 0
        budget_score = 1.0 if budget == 0 else max(0.0, 1 - max(0, total_expenses - budget) / budget)
        goal_score = 0.5
        if len(goals_df) > 0:
            prog = []
            for _, r in goals_df.iterrows():
                targ = float(r.get("TargetAmount",0) or 0)
                saved = float(r.get("SavedSoFar",0) or 0)
                prog.append(1.0 if targ <= 0 else min(1.0, saved/targ))
            goal_score = sum(prog)/len(prog)
        final_score = int(max(0, min(100, round((0.45*savings_rate + 0.3*budget_score + 0.25*goal_score) * 100))))
        return final_score

    score = compute_smartscore(total_income, total_expenses, total_investments, budget, df_goal)

    # Next month estimated savings
    avg_monthly_exp = df_exp.groupby(df_exp["Date"].dt.to_period("M"))["Amount"].sum().mean() if not df_exp.empty else 0
    avg_monthly_inc = df_inc.groupby(df_inc["Date"].dt.to_period("M"))["Amount"].sum().mean() if not df_inc.empty else 0
    next_month_savings = max(0.0, avg_monthly_inc - avg_monthly_exp - total_investments)

    # ---------- METRICS CARDS ----------
    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Income", currency_format(total_income))
    col2.metric("🛒 Total Expenses", currency_format(total_expenses))
    col3.metric("💳 Investments", currency_format(total_investments))
    col4.metric("💡 Savings", currency_format(total_savings))

    st.subheader("💡 SmartScore & Future Savings")
    col1, col2 = st.columns(2)
    col1.metric("SmartScore (0-100)", f"{score}")
    col2.metric("Estimated Next Month Savings", currency_format(next_month_savings))

    # ---------- MONTHLY BUDGET PROGRESS ----------
    st.subheader("📅 Monthly Budget")
    if budget > 0:
        used = min(1.0, this_month_exp / budget)
        st.progress(used)
        st.write(f"Spent: **{currency_format(this_month_exp)}** / {currency_format(budget)}")
        if this_month_exp > budget:
            st.error("⚠️ Over budget!")
        elif this_month_exp > 0.8 * budget:
            st.warning("🔶 Close to limit.")
        else:
            st.success("🟢 You’re doing great!")
    else:
        st.info("⚠️ Set a monthly budget in Settings to start tracking.")

    # ---------- CATEGORY BREAKDOWN PIE CHART ----------
    st.markdown("### 📌 Category Breakdown")
    if not df_exp.empty:
        cat_summary = df_exp.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(
            cat_summary,
            names="Category",
            values="Amount",
            hole=0.3,
            hover_data=["Amount"],
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig.update_traces(
            hoverinfo="label+percent+value",
            textinfo="percent",
            pull=[0.05]*len(cat_summary),
            marker=dict(line=dict(color='#000000', width=2))
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#00fff7',
            margin=dict(t=0,b=0,l=0,r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses to show yet.")

    # ---------- INCOME VS EXPENSES TREND ----------
    st.markdown("### 📉 Income vs Expenses (Recent Months)")
    merged = pd.DataFrame({
        "Expenses": df_exp.tail(12)["Amount"].reset_index(drop=True) if not df_exp.empty else [],
        "Income": df_inc.tail(12)["Amount"].reset_index(drop=True) if not df_inc.empty else []
    }).fillna(0)
    st.line_chart(merged)

    # ---------- RECENT ACTIVITY ----------
    st.markdown("### 🔍 Recent Activity")
    combined = pd.concat([
        df_inc.assign(Type="Income") if not df_inc.empty else pd.DataFrame(),
        df_exp.assign(Type="Expense") if not df_exp.empty else pd.DataFrame(),
        df_inv.assign(Type="Investment") if not df_inv.empty else pd.DataFrame()
    ], ignore_index=True)

    if not combined.empty:
        st.dataframe(combined.sort_values(by="Date", ascending=False).head(10), use_container_width=True)
    else:
        st.info("No data recorded yet.")

    # ---------- ACHIEVEMENTS & BADGES ----------
    st.subheader("🏅 Achievements & Milestones")
    if total_savings >= 10000:
        st.success("🎉 Saved First 10k!")
    if score >= 80:
        st.success("💪 Excellent SmartScore!")
    if not df_goal.empty and all(df_goal["SavedSoFar"] >= df_goal["TargetAmount"]):
        st.success("🏆 All Goals Completed!")
    if total_expenses > total_income:
        st.warning("⚠️ Expenses exceeded income this month!")

# ---------------------------
# Add Expense
# ---------------------------
elif st.session_state.page == "Add Expense":
    st.header("➕ Add Expense")

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

    with st.form("add_exp", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            exp_date = st.date_input("Date", value=date.today())
            exp_desc = st.text_input("Note (e.g., Coffee, Rent)")
        with col2:
            exp_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            exp_cat = st.selectbox("Category", ["Food","Transport","Shopping","Bills","Entertainment","Health","Education","Other"])

        submitted = st.form_submit_button("💾 Save Expense")

    if submitted:
        if exp_desc and exp_amount > 0:
            new = {"Date": exp_date, "Category": exp_cat, "Note": exp_desc, "Amount": float(exp_amount)}
            df = pd.read_csv(EXP_FILE)  # <-- bypass cache
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            df.to_csv(EXP_FILE, index=False)

            st.success(f"Added successfully — {currency_format(float(exp_amount))}")

            # reload table immediately
            df = pd.read_csv(EXP_FILE)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            st.markdown("### ✅ Latest expenses")
            st.dataframe(df.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
        else:
            st.warning("Please enter a note/description and an amount greater than 0.")


# ---------------------------
# Add Income
# ---------------------------
elif st.session_state.page == "Add Income":
    st.header("➕ Add Income")
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

    with st.form("add_inc", clear_on_submit=True):
        inc_date = st.date_input("Date", value=date.today())
        inc_source = st.text_input("Source (e.g., Salary, Business)")
        inc_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Income")
        
        if submitted:
            if inc_source.strip() != "" and inc_amount > 0:
                # Prepare new entry with consistent date format
                new_entry = {
                    "Date": pd.to_datetime(inc_date).strftime("%Y-%m-%d"),
                    "Source": inc_source.strip(),
                    "Amount": float(inc_amount)
                }
                
                # Load existing incomes or create empty dataframe
                if os.path.exists(INC_FILE):
                    df_inc = pd.read_csv(INC_FILE)
                else:
                    df_inc = pd.DataFrame(columns=["Date", "Source", "Amount"])
                
                # Append new entry
                df_inc = pd.concat([df_inc, pd.DataFrame([new_entry])], ignore_index=True)
                
                # Save back to CSV
                df_inc.to_csv(INC_FILE, index=False)
                
                st.success(f"Income of {currency_format(inc_amount)} from '{inc_source}' added ✅")
                
                # Go back to dashboard immediately
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.warning("Please enter a valid source and amount greater than 0.")


# ---------------------------
# Add Investment
# ---------------------------
elif st.session_state.page == "Add Investment":
    st.header("➕ Add Investment")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

    with st.form("add_inv", clear_on_submit=True):
        inv_date = st.date_input("Date", value=date.today())
        inv_type = st.selectbox("Investment Type", ["Stocks","Mutual Funds","Crypto","Gold","Real Estate","Other"])
        inv_amount = st.number_input("Amount Invested", min_value=0.0, format="%.2f")
        inv_current = st.number_input("Current Value (optional)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Investment")
        if submitted:
            cur_val = float(inv_current) if inv_current > 0 else float(inv_amount)
            new = {"Date": inv_date, "Type": inv_type, "Amount": float(inv_amount), "CurrentValue": cur_val}
            df = load_csv(INV_FILE)
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_csv(df, INV_FILE)
            st.success("Investment added ✅")
            st.session_state.page = "Dashboard"
            st.rerun()

# ---------------------------
# View Expenses
# ---------------------------
elif st.session_state.page == "View Expenses":
    st.header("📋 View Expenses")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

    df = pd.read_csv(EXP_FILE)  # <-- bypass cached load
    if df.empty:
        st.info("No expenses yet.")
    else:
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
        st.markdown("**Delete rows:** Enter row index to delete below.")
        idx = st.number_input("Row index (0-based)", min_value=0, step=1)
        if st.button("Delete row"):
            df = df.reset_index(drop=True)
            if 0 <= idx < len(df):
                df = df.drop(index=int(idx)).reset_index(drop=True)
                df.to_csv(EXP_FILE, index=False)
                st.success("Row deleted.")
                st.rerun()
            else:
                st.warning("Index out of range.")

# ---------------------------
# Goals
# ---------------------------
if st.session_state.page == "Goals":
    st.header("🎯 Goals")
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    # --- Create / Update Goal ---
    st.subheader("➕ Create / Update Goal")
    g_name = st.text_input("Goal Name (e.g., New Phone)", key="goal_name")
    g_target = st.number_input("Target Amount", min_value=0.0, format="%.2f", key="goal_target")
    g_saved = st.number_input("Already Saved", min_value=0.0, format="%.2f", key="goal_saved")
    g_date = st.date_input("Target Date", value=date.today(), key="goal_date")
    
    if st.button("Create / Update Goal"):
        df = pd.read_csv(GOAL_FILE)
        g_date_str = g_date.strftime("%Y-%m-%d")
        if g_name in df["Name"].values if not df.empty else False:
            df.loc[df["Name"]==g_name, ["TargetAmount","SavedSoFar","TargetDate"]] = [g_target, g_saved, g_date_str]
        else:
            df = pd.concat([df, pd.DataFrame([{
                "Name": g_name,
                "TargetAmount": g_target,
                "SavedSoFar": g_saved,
                "TargetDate": g_date_str
            }])], ignore_index=True)
        df.to_csv(GOAL_FILE, index=False)
        st.success("Goal saved.")
        st.rerun()
    
    # --- Load latest data for allocation ---
    df_exp = pd.read_csv(EXP_FILE)
    df_inc = pd.read_csv(INC_FILE)
    df_inv = pd.read_csv(INV_FILE)
    df_goals = pd.read_csv(GOAL_FILE)

    total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
    total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
    total_investments = (
        df_inv["CurrentValue"].sum()
        if ("CurrentValue" in df_inv.columns and not df_inv.empty)
        else df_inv["Amount"].sum()
        if not df_inv.empty
        else 0.0
    )

    # --- Available savings and remaining allocation ---
    available_savings = max(0.0, total_income - total_expenses - total_investments)
    allocated_to_goals = df_goals["SavedSoFar"].sum() if not df_goals.empty else 0.0
    remaining_savings = max(0.0, available_savings - allocated_to_goals)

    # --- Display Goals ---
    if not df_goals.empty:
        st.subheader("📌 Your Goals")
        for i, row in df_goals.iterrows():
            name = row["Name"]
            targ = float(row.get("TargetAmount", 0))
            saved = float(row.get("SavedSoFar", 0))
            pct = saved / targ if targ > 0 else 1.0

            st.markdown(f"**{name}** — {currency_format(saved)} / {currency_format(targ)}")
            st.progress(min(1.0, pct))

            add_amt = st.number_input(
                f"Add amount to {name}",
                min_value=0.0,
                max_value=remaining_savings,
                format="%.2f",
                key=f"add_{i}"
            )

            # Only run allocation logic when button is pressed
            if st.button(f"Add to {name}", key=f"btn_{i}"):
                if add_amt <= 0:
                    st.warning("Enter an amount greater than 0.")
                elif add_amt > remaining_savings:
                    st.error(
                        f"⚠️ You don’t have enough remaining savings! You can allocate up to {currency_format(remaining_savings)}"
                    )
                else:
                    # Valid allocation
                    df_goals.loc[i, "SavedSoFar"] += add_amt
                    df_goals.to_csv(GOAL_FILE, index=False)
                    st.success(f"Added {currency_format(add_amt)} to {name} ✅")

                    # Update remaining savings for other goals
                    remaining_savings -= add_amt
                    st.rerun()
    else:
        st.info("No goals yet. Create one above to start saving for your future!")

# ---------------------------
# AI Coach
# ---------------------------
elif st.session_state.page == "AI Coach":
    st.header("🤖 AI Coach (Placeholder)")
    st.write("Integration with a chatbot coming soon.")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

# ---------------------------
# Settings
# ---------------------------
elif st.session_state.page == "Settings":
    st.header("⚙️ Settings")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

    c1,c2 = st.columns(2)
    with c1:
        cur = st.selectbox("Currency", ["SAR","USD","INR","EUR","CAD"], index=["SAR","USD","INR","EUR","CAD"].index(st.session_state.currency))
        st.session_state.currency = cur
    with c2:
        mb = st.number_input("Monthly Budget", min_value=0.0, format="%.2f", value=st.session_state.monthly_budget)
        if st.button("Save Settings"):
            st.session_state.monthly_budget = float(mb)
            settings["currency"] = st.session_state.currency
            settings["monthly_budget"] = float(mb)
            save_settings(settings)
            st.success("Settings saved ✔️")
            st.rerun()