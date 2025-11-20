# ---------------------------
# Page rendering
# ---------------------------
page = st.session_state.page

# ---------------------------
# Landing Page
# ---------------------------
if page == "Landing":
    # Top-right buttons
    col1,col2,col3,col4 = st.columns([4,4,2,2])
    with col3:
        if st.button("🚀 Try for Free"):
            st.session_state.page="Dashboard"; st.rerun()
    with col4:
        if st.button("🔒 Login"):
            st.session_state.page="login"; st.rerun()
    
    # Hero section
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

# ---------------------------
# Login Page
# ---------------------------
elif page == "login":
    apply_css("Landing")
    st.markdown("<div style='text-align:center; margin-top:150px;'>"
                "<h1 class='neon'>🔒 Login to SmartSpend</h1>"
                "<h3 class='neon-small'>Enter credentials to access your dashboard</h3>"
                "</div>", unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if username and password:
            st.session_state.page="Dashboard"
            st.success("Logged in successfully!"); st.rerun()
        else:
            st.error("Enter valid credentials")
    if st.button("⬅️ Back"):
        st.session_state.page="Landing"; st.rerun()

# ---------------------------
# Dashboard
# ---------------------------
elif page == "Dashboard":
    apply_css("Dashboard")

    st.title("💸 SmartSpend Dashboard")

    # Reload CSVs fresh
    df_exp = pd.read_csv(EXP_FILE)
    df_inc = pd.read_csv(INC_FILE)
    df_inv = pd.read_csv(INV_FILE)
    df_goal = pd.read_csv(GOAL_FILE)

    # Ensure Date column is datetime
    for d in [df_exp, df_inc, df_inv]:
        if not d.empty and "Date" in d.columns:
            d["Date"] = pd.to_datetime(d["Date"], errors="coerce")

    # ---------- Calculations ----------
    total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0.0
    total_income = df_inc["Amount"].sum() if not df_inc.empty else 0.0
    total_investments = df_inv["CurrentValue"].sum() if ("CurrentValue" in df_inv.columns and not df_inv.empty) else df_inv["Amount"].sum() if not df_inv.empty else 0.0
    total_savings = max(0.0, total_income - total_expenses - total_investments)

    now = datetime.now()
    this_month_exp = df_exp[(df_exp["Date"].dt.month == now.month) & (df_exp["Date"].dt.year == now.year)]["Amount"].sum() if (not df_exp.empty and df_exp["Date"].notna().all()) else 0.0

    budget = st.session_state.monthly_budget

    # ---------- SmartScore ----------
    score = compute_smartscore(total_income, total_expenses, total_investments, budget, df_goal)

    # ---------- Metric Cards ----------
    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", currency_format(total_income))
    col2.metric("Total Expenses", currency_format(total_expenses))
    col3.metric("Investments", currency_format(total_investments))
    col4.metric("Savings", currency_format(total_savings))

    # SmartScore
    st.subheader("💡 SmartScore")
    st.metric("SmartScore (0-100)", f"{score}")

    # Monthly Budget
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

    # Tip based on score
    if score < 50:
        st.warning("💡 Tip: Try reducing spending or increasing savings to boost your score.")
    elif score < 80:
        st.info("💡 You're doing good! A little more savings can make it great.")
    else:
        st.success("🔥 Amazing! You're handling money like a pro!")

    # ---------- Graphs ----------
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

    # Income vs Expenses
    st.markdown("### 📉 Income vs Expenses (Recent)")
    merged = pd.DataFrame({
        "Expenses": df_exp.tail(12)["Amount"].reset_index(drop=True) if not df_exp.empty else [],
        "Income": df_inc.tail(12)["Amount"].reset_index(drop=True) if not df_inc.empty else []
    }).fillna(0)
    st.line_chart(merged)

    # Recent Activity
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