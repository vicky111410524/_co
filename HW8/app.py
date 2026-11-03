from datetime import date

import gspread
import pandas as pd
import plotly.express as px
import streamlit as st
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

st.set_page_config(page_title="雲端記帳本", layout="wide")

SPREADSHEET_NAME = "MyExpenseDB"
USERS_SHEET = "Users"
EXPENSES_SHEET = "Expenses"
USER_COLUMNS = ["username", "password"]
EXPENSE_COLUMNS = ["id", "username", "date", "category", "item", "amount"]
CATEGORIES = ["飲食", "交通", "購物", "娛樂", "生活", "醫療", "教育", "其他"]


@st.cache_resource(show_spinner="正在連線至 Google 試算表...")
def get_client():
    credentials = dict(st.secrets["gcp_service_account"])
    if "private_key" in credentials:
        credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")
    return gspread.service_account_from_dict(credentials)


@st.cache_resource(show_spinner=False)
def get_spreadsheet():
    return get_client().open(SPREADSHEET_NAME)


def get_worksheet(name, headers):
    spreadsheet = get_spreadsheet()
    try:
        worksheet = spreadsheet.worksheet(name)
    except WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers))
        worksheet.append_row(headers)
        return worksheet

    if not worksheet.row_values(1):
        worksheet.append_row(headers)
    return worksheet


def get_users_worksheet():
    return get_worksheet(USERS_SHEET, USER_COLUMNS)


def get_expenses_worksheet():
    return get_worksheet(EXPENSES_SHEET, EXPENSE_COLUMNS)


def authenticate(username, password):
    records = get_users_worksheet().get_all_records()
    return any(
        str(record.get("username", "")).strip() == username
        and str(record.get("password", "")) == password
        for record in records
    )


def register_user(username, password):
    worksheet = get_users_worksheet()
    records = worksheet.get_all_records()
    if any(str(record.get("username", "")).strip() == username for record in records):
        return False
    worksheet.append_row([username, password])
    return True


def next_expense_id(records):
    ids = []
    for record in records:
        try:
            ids.append(int(float(record.get("id", 0))))
        except (TypeError, ValueError):
            continue
    return max(ids, default=0) + 1


def add_expense(username, expense_date, category, item, amount):
    worksheet = get_expenses_worksheet()
    records = worksheet.get_all_records()
    worksheet.append_row(
        [
            next_expense_id(records),
            username,
            str(expense_date),
            category,
            item,
            float(amount),
        ]
    )


def load_user_expenses(username):
    records = get_expenses_worksheet().get_all_records()
    dataframe = pd.DataFrame(records, columns=EXPENSE_COLUMNS)
    if dataframe.empty:
        return dataframe

    dataframe = dataframe[
        dataframe["username"].astype(str).str.strip() == username
    ].copy()
    if dataframe.empty:
        return dataframe

    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")
    dataframe["amount"] = pd.to_numeric(dataframe["amount"], errors="coerce").fillna(0.0)
    dataframe = dataframe.dropna(subset=["date"])
    return dataframe.sort_values("date")


def render_auth():
    st.title("雲端記帳本")
    st.caption("請先登入，或建立一個新帳號。")

    login_tab, register_tab = st.tabs(["登入", "註冊"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("帳號")
            password = st.text_input("密碼", type="password")
            login_submitted = st.form_submit_button("登入", use_container_width=True)

        if login_submitted:
            username = username.strip()
            if not username or not password:
                st.warning("請輸入帳號與密碼。")
            elif authenticate(username, password):
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("帳號或密碼錯誤。")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("新帳號")
            new_password = st.text_input("新密碼", type="password")
            confirm_password = st.text_input("確認密碼", type="password")
            register_submitted = st.form_submit_button("註冊", use_container_width=True)

        if register_submitted:
            new_username = new_username.strip()
            if not new_username or not new_password:
                st.warning("請輸入帳號與密碼。")
            elif new_password != confirm_password:
                st.error("兩次輸入的密碼不一致。")
            elif register_user(new_username, new_password):
                st.success("註冊成功，請切換到「登入」分頁。")
            else:
                st.error("此帳號已存在。")


def render_sidebar(username):
    with st.sidebar:
        st.subheader("目前使用者")
        st.info(username)
        st.divider()
        st.subheader("新增紀錄")

        with st.form("add_expense_form", clear_on_submit=True):
            expense_date = st.date_input("日期", value=date.today())
            category = st.selectbox("分類", CATEGORIES)
            item = st.text_input("項目")
            amount = st.number_input("金額", min_value=0.0, step=1.0, format="%.0f")
            submitted = st.form_submit_button("新增", use_container_width=True)

        if submitted:
            item = item.strip()
            if not item:
                st.warning("請輸入項目名稱。")
            elif amount <= 0:
                st.warning("金額必須大於 0。")
            else:
                add_expense(username, expense_date, category, item, amount)
                st.success("已新增紀錄。")
                st.rerun()

        st.divider()
        if st.button("登出", use_container_width=True):
            st.session_state["username"] = None
            st.rerun()


def render_dashboard(username):
    st.title("雲端記帳本")
    st.caption(f"目前登入：{username}")

    dataframe = load_user_expenses(username)

    if dataframe.empty:
        st.info("目前尚無記帳資料，請從左側新增第一筆紀錄。")
        return

    total = dataframe["amount"].sum()
    average = dataframe["amount"].mean()

    metric_columns = st.columns(3)
    metric_columns[0].metric("總支出", f"NT$ {total:,.0f}")
    metric_columns[1].metric("紀錄筆數", f"{len(dataframe)} 筆")
    metric_columns[2].metric("平均每筆", f"NT$ {average:,.0f}")

    st.divider()

    left, right = st.columns(2)

    category_summary = (
        dataframe.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )
    pie = px.pie(
        category_summary,
        names="category",
        values="amount",
        title="類別支出比例",
        hole=0.4,
    )
    left.plotly_chart(pie, use_container_width=True)

    daily_summary = (
        dataframe.groupby("date", as_index=False)["amount"].sum().sort_values("date")
    )
    trend = px.line(
        daily_summary,
        x="date",
        y="amount",
        markers=True,
        title="每日支出趨勢",
    )
    trend.update_layout(xaxis_title="日期", yaxis_title="金額")
    right.plotly_chart(trend, use_container_width=True)

    st.subheader("記帳紀錄")
    display_dataframe = dataframe.sort_values("date", ascending=False).copy()
    display_dataframe["date"] = display_dataframe["date"].dt.strftime("%Y-%m-%d")
    display_dataframe = display_dataframe[["date", "category", "item", "amount"]]
    display_dataframe = display_dataframe.rename(
        columns={"date": "日期", "category": "分類", "item": "項目", "amount": "金額"}
    )
    st.dataframe(display_dataframe, use_container_width=True, hide_index=True)


def main():
    if "username" not in st.session_state:
        st.session_state["username"] = None

    try:
        has_credentials = "gcp_service_account" in st.secrets
    except Exception:
        has_credentials = False

    if not has_credentials:
        st.error(
            "尚未設定 st.secrets['gcp_service_account']，"
            "請新增 .streamlit/secrets.toml 並填入服務帳戶憑證。"
        )
        st.stop()

    try:
        get_spreadsheet()
    except SpreadsheetNotFound:
        st.error(
            f"找不到名為「{SPREADSHEET_NAME}」的 Google 試算表，"
            "請確認試算表已建立並分享給服務帳戶。"
        )
        st.stop()
    except Exception as error:
        st.error(f"無法連線至 Google 試算表：{error}")
        st.stop()

    username = st.session_state.get("username")

    if not username:
        render_auth()
        return

    render_sidebar(username)
    render_dashboard(username)


if __name__ == "__main__":
    main()
