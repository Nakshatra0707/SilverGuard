import streamlit as st
import pandas as pd
import time
import gridfs
from bson.objectid import ObjectId
from pymongo import MongoClient
from deep_translator import GoogleTranslator, DeeplTranslator
from gtts import gTTS
from openai import OpenAI

api_key = st.secrets["openai"]["api_key"]

finance = OpenAI(
    api_key = api_key
)


languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-cn",
    "Hindi": "hi"
}

connection_string = st.secrets["mongo"]["connection_string"]

client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
db = client['Strawberry_Innovation']
fs = gridfs.GridFS(db)
collection = db['Users']

if 'bank_statement' not in st.session_state:
    st.session_state.bank_statement = None

if 'name' not in st.session_state:
    st.session_state.name = None

if 'password' not in st.session_state:
    st.session_state.password = None

if 'age' not in st.session_state:
    st.session_state.age = ""

if 'insurance' not in st.session_state:
    st.session_state.insurance = None

if 'identity_proof' not in st.session_state:
    st.session_state.identity_proof = None

if 'user' not in st.session_state:
    st.session_state.user = None

tabs = st.tabs(["Home", "Financial Details", "Advice", "News", "Register", "Sign-in"])


st.markdown("""
    <style>
        .home-title {
            font-size: 2.5em;
            color: #004d99;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .home-header {
            font-size: 2em;
            color: #003366;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .home-text {
            font-size: 1.2em;
            color: #333333;
            line-height: 1.6;
            text-align: center;
            margin: 0;
        }
        .stButton {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #004d99;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #003366;
        }
        .main {
            background: linear-gradient(#003366, #F5F5DC);
            padding: 20px;
            height: 100vh;
            color: #333333;
        }
    </style>
""", unsafe_allow_html=True)


if 'language' not in st.session_state:
    st.session_state.language = 'en'  


with tabs[0]:  # Home Page
    st.markdown('<div>', unsafe_allow_html=True)

    st.image("logo.png")
    
    if st.button("Hindi"):
        st.session_state.language = 'hi'
    elif st.button("English"):
        st.session_state.language = 'en'

    title = "Silver Guard: "
    header = "About Us"
    text = "Silver Guard empowers elderly and disabled users with effortless financial management. It combines personalized advice, family oversight, and proactive cybersecurity, making digital finance secure, simple, and supportive."

    google_translator = GoogleTranslator(source='auto', target='hi')
    translated_title = google_translator.translate(title)
    translated_header = google_translator.translate(header)
    translated_about_text = google_translator.translate(text)
    
    if st.session_state.language == 'en':
        st.markdown(f'<p class="home-title">{title}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="home-header">{header}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="home-text">{text}</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="home-title">{translated_title}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="home-header">{translated_header}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="home-text">{translated_about_text}</p>', unsafe_allow_html=True)

    if st.session_state.language == "en":
        if st.button("Text to Speech - English"):
            combined_text = f"{title}. {header}. {text}"
            tts = gTTS(text=combined_text, lang='en')
            tts.save("combined_text.mp3")
            st.audio("combined_text.mp3")

    else:    
        if st.button("Text to Speech - Hindi"):
            combined_text = f"{translated_title}. {translated_header}. {translated_about_text}"
            tts = gTTS(text=combined_text, lang='hi')
            tts.save("combined_text.mp3")
            st.audio("combined_text.mp3")

    
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:  # Displaying Financial Details
    st.title("Financial Details")
    if st.button("View Details!"):
        if st.session_state.user is not None:
            st.write("Bank Statement:")
            if st.session_state.bank_statement:
                try:
                    file = fs.get(st.session_state.bank_statement)
                    st.write(f"File {file.filename} retrieved.")
                    st.download_button("Download Bank Statement", file.read(), file_name=file.filename)
                except gridfs.errors.NoFile:
                    st.write("File not found")
            
            st.write("Insurance Documents")
            if st.session_state.insurance:
                for id in st.session_state.insurance:
                    try:
                        file = fs.get(id)
                        st.write(f"File {file.filename} retrieved.")
                        st.download_button("Download Insurance Document", file.read(), file_name=file.filename)
                    except gridfs.errors.NoFile:
                        st.write("File not found.")

            st.write("Identity Proof Documents")
            if st.session_state.identity_proof:
                for id in st.session_state.identity_proof:
                    try:
                        file = fs.get(id)
                        st.write(f"File {file.filename} retrieved.")
                        st.download_button("Download Identity Proof", file.read(), file_name=file.filename)
                    except gridfs.errors.NoFile:
                        st.write("File not found.")

def form_validity(name, age, bank_statement, insurance, identity_proof):
    return bool(name) and bool(age) and bool(bank_statement) and bool(insurance) and bool(identity_proof)

with tabs[4]:  # Register Tab - uploading documents
    st.header("Register")
    st.write("Already registered? Try the sign-in tab instead.")
    name = st.text_input("What's your name?")
    password = st.text_input("What's your password? (minimum length is 8)")
    age = st.text_input("What's your age?")
    bank_statement = st.file_uploader("Upload your bank statement (pdf)", accept_multiple_files=False, type=['pdf'], key="Bank Statement")
    insurance = st.file_uploader("Upload your Insurance Documents (pdf)", accept_multiple_files=True, type=['pdf'], key='Insurance')
    identity_proof = st.file_uploader("Upload your Identity Proof (Aadhar/Pan) (pdf)", accept_multiple_files=True, type=['pdf'], key='Identity')

    name_exists = collection.find_one({"name": name}) is not None
    error_message = st.empty()
    if name_exists:
        error_message.error("The name already exists!")
    else:
        error_message.empty()

    valid = form_validity(name, age, bank_statement, insurance, identity_proof)

    if st.button("Register!"):
        if name_exists:
            st.error("That name already exists!")
        elif len(name) < 5:
            st.error("Username has to be at least 5 characters")
        elif not valid:
            st.error("Please upload all required documents")
        elif len(password) < 8:
            st.error("Password is too short!")
        else:
            with st.spinner("Submitting..."):
                time.sleep(1)
            with st.spinner("Creating profile..."):
                time.sleep(2)

            bank_statement_id = fs.put(bank_statement, filename="bank_statement.pdf") if bank_statement else None
            insurance_ids = [fs.put(file, filename=file.name) for file in insurance] if insurance else []
            identity_proof_ids = [fs.put(file, filename=file.name) for file in identity_proof] if identity_proof else []

            collection.insert_one({
                "name": name,
                "password": password,
                "age": age,
                "bank_statement": bank_statement_id,
                "insurance": insurance_ids,
                "identity_proof": identity_proof_ids
            })

            st.success("Profile Created!")
            st.session_state.name = name
            st.session_state.user = collection.find_one({"name": st.session_state.name})
            st.session_state.age = st.session_state.user.get("age")
            st.session_state.bank_statement = st.session_state.user.get("bank_statement")
            st.session_state.insurance = st.session_state.user.get("insurance")
            st.session_state.identity_proof = st.session_state.user.get("identity_proof")

with tabs[5]:  # Sign in
    st.header("Sign-in")
    st.write("Haven't created an account? Try the Register page.")
    name = st.text_input("Username", key="sign_in_name")
    entered_password = st.text_input("Password", key="sign_in_password")

    temp_user = collection.find_one({"name": name})
    name_exists = False
    password_is_correct = False

    if temp_user:
        name_exists = True
        if (entered_password == temp_user.get("password")):
            password_is_correct = True

    valid = name_exists and password_is_correct and bool(name) and bool(entered_password)

    if st.button("Sign-in!"):
        with st.spinner("Checking username and password...."):
            time.sleep(2)
        if not valid:
            st.error("Incorrect username or password.")
        else:
            st.session_state.name = name
            st.session_state.user = collection.find_one({"name": st.session_state.name})
            st.session_state.age = st.session_state.user.get("age")
            st.session_state.password = st.session_state.user.get("password")
            st.session_state.bank_statement = st.session_state.user.get("bank_statement")
            st.session_state.insurance = st.session_state.user.get("insurance")
            st.session_state.identity_proof = st.session_state.user.get("identity_proof")
            with st.spinner("Logging in....."):
                time.sleep(2)
            st.success("Logged in!")


with tabs[2]: # Financial Advice

    prompt = st.text_input("Enter prompt: ")
    if st.button("Get financial advice!"):
        response = finance.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {"role":"user", "content":f"give financial advice like mike ross for the following prompt: {prompt}"}
        ]
    )

        message = response.choices[0].message.content
        st.write(message)

with tabs[3]: # News
    st.title("'Stock market scam': 2 senior citizens lose Rs 96 lakh in Maharashtra:")
    st.write(
        """

Two senior citizens, one from Thane and the other from Navi Mumbai, collectively lost Rs 96 lakh this week in what the Maharashtra Police are claiming to be a ‘stock market scam’.

In the Thane case, a 65-year-old man, who recently retired as an administrator, wanted to invest his life savings in the share market. In May, when he was watching videos online, he saw an ‘IIFL’ advertisement. Assuming it to be the real investment company, he sent a text message to the number provided in the advertisement. The person then added him to a WhatsApp group.

Earlier this month, the man approached Thane police and an FIR was registered against unknown accused on Tuesday."
    """)
