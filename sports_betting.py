import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
from collections import Counter

# ---------------------
# セッション管理
# ---------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "tottei_id" not in st.session_state:
    st.session_state.tottei_id = ""

# ---------------------
# Google Sheets 認証
# ---------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GSPREAD_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1i7aGvgKURjx9wZlz7txRcpweYa_zo-0sT08ekCZFRYA/edit")
worksheet = sh.worksheet("シート1")

# ---------------------
# ページ設定
# ---------------------
st.set_page_config(page_title="PLAY OFFS パブリックビューイング", layout="wide")

# ---------------------
# 認証ページ
# ---------------------
def auth_page():
    st.title("🔐 NBA PLAYOFFS勝敗予想 認証")
    st.write("TOTTEIアプリに表示されているIDと合言葉、ニックネームを入力してください。")

    input_id = st.text_input(
        "TOTTEIアプリのトップ画面に表示されている「TOTTEI ID」を入力してください。（例：1000001234 の場合 → 1234）", 
        key="auth_id"
    )
    nickname_input = st.text_input("ニックネーム（結果発表時にお呼びします）", key="nickname_input")
    password = st.text_input("合言葉（チラシをご確認ください）", value="")


    if st.button("認証して予想へ進む"):
        if input_id.strip() and nickname_input.strip() and password.strip():
            if password.strip().lower() == "カリー":
                st.session_state.authenticated = True
                st.session_state.tottei_id = input_id.strip()
                st.session_state.nickname = nickname_input.strip()
            else:
                st.error("合言葉が違います。")
        else:
            st.warning("TOTTEI ID・ニックネーム・合言葉のすべてを入力してください。")


# ---------------------
# ベッティングページ
# ---------------------
def betting_page():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap" rel="stylesheet">
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0a0f2c;
            color: white;
            font-family: 'Roboto Mono', monospace !important;
        }
        h1, h2, h3, h4, h5, h6, p, div, span, label {
            color: white !important;
        }
        input, textarea {
            color: white !important;
            background-color: #1e293b !important;
            border: 1px solid #94a3b8;
            border-radius: 4px;
            padding: 12px;
        }
        button {
            background-color: #f87171 !important;
            color: black !important;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
        }
        .bet-card {
            background-color: #111827;
            border: 2px solid #22c55e;
            border-radius: 10px;
            padding: 2rem;
            margin-top: 2rem;
            box-shadow: 0 0 12px rgba(34, 197, 94, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### PLAY OFFS パブリックビューイング in GLION ARENA KOBE")
    st.image("https://files.totteikobe.jp/2025/04/Playoffs_Keyart_Horiz_1920x1080_20250505.jpg")

    # 対戦カード
    st.markdown("## 5月10日の対戦カード")
    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        st.markdown("""
            <div style='text-align: center;'>
                <img src='https://a.espncdn.com/i/teamlogos/nba/500/MIN.png' width='150'>
                <h4>ミネソタ・ティンバーウルブズ</h4>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 100px;'>
                <h2>VS</h2>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div style='text-align: center;'>
                <img src='https://a.espncdn.com/i/teamlogos/nba/500/gsw.png' width='150'>
                <h4>ゴールデンステート・ウォリアーズ</h4>
            </div>
        """, unsafe_allow_html=True)

    # ベットカード
    st.markdown("""<div class="bet-card"><h2>勝者とスコアを予想しよう！</h2>""", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center;'>勝者を選択してください</h3>", unsafe_allow_html=True)
    
    # ✅ ラジオボタン中央寄せ（このブロックを差し込む）
    st.markdown("""
    <div style='display: flex; justify-content: center;'>
        <div>
    """, unsafe_allow_html=True)
    
    predicted_winner = st.radio(
        label="",
        options=["ミネソタ・ティンバーウルブズ", "ゴールデンステート・ウォリアーズ"],
        horizontal=True,
        key="winner_radio"
    )
    
    st.markdown("</div></div>", unsafe_allow_html=True)



    if predicted_winner:
        st.markdown(f"<p style='text-align:center;'>あなたの選択：<b style='color:#f87171'>{predicted_winner}</b></p>", unsafe_allow_html=True)

    st.markdown("<br><h3 style='text-align:center;'>予想スコアを入力してください</h3>", unsafe_allow_html=True)
    col4, col5 = st.columns(2)
    with col4:
        okc_input = st.text_input("ウルブズの得点予想", key="okc_score_input")
        okc_score = int(okc_input) if okc_input.isdigit() else None
    with col5:
        den_input = st.text_input("ウォリアーズの得点予想", key="den_score_input")
        den_score = int(den_input) if den_input.isdigit() else None

    # 提出処理
    submit = st.button("この内容で予想を提出", use_container_width=True)
    if submit:
        if predicted_winner and okc_score is not None and den_score is not None:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([
                now,
                st.session_state.tottei_id,
                st.session_state.nickname,
                predicted_winner,
                okc_score,
                den_score
            ])

            st.success(f"""✅ 送信完了！  
TOTTEI ID：**{st.session_state.tottei_id}**  
あなたの予想：**{predicted_winner} の勝利**  
予想スコア：ウルブズ {okc_score} - {den_score} ウォリアーズ""")

            try:
                data = worksheet.get_all_records()
                winner_counts = Counter([row['勝者予想'] for row in data])
                okc_scores = [int(row['ウルブズスコア']) for row in data if str(row['ウルブズスコア']).isdigit()]
                den_scores = [int(row['ウォリアーズスコア']) for row in data if str(row['ウォリアーズスコア']).isdigit()]
                avg_okc = round(sum(okc_scores) / len(okc_scores), 1) if okc_scores else "-"
                avg_den = round(sum(den_scores) / len(den_scores), 1) if den_scores else "-"

                st.markdown("---")
                st.markdown("### 📊 みんなの予想集計")
                st.markdown(f"- ウルブズ勝利予想：{winner_counts.get('ミネソタ・ティンバーウルブズ', 0)}件")
                st.markdown(f"- ウォリアーズ勝利予想：{winner_counts.get('ゴールデンステート・ウォリアーズ', 0)}件")
                st.markdown(f"- 平均予想スコア：ウルブズ {avg_okc} - {avg_den} ウォリアーズ")
            except Exception as e:
                st.error(f"集計データの取得に失敗しました: {e}")
        else:
            st.warning("全ての項目を正しく入力してください。")

    st.markdown("</div>", unsafe_allow_html=True)  # .bet-card 終了

# ---------------------
# 実行フロー制御
# ---------------------
if not st.session_state.authenticated:
    auth_page()
else:
    betting_page()
