import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Custom CSS for fonts and centering image
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400&family=Lexend:wght@600&display=swap');
    .title-font {
        font-family: 'Lexend', sans-serif;
        font-size: 36px;
        text-align: center;
    }
    .paragraph-font {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        text-align: justify;
    }
    .center-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# Title with custom font
st.markdown('<p class="title-font">TRADUCTOR</p>', unsafe_allow_html=True)
st.markdown('<p class="paragraph-font">Escucho lo que quieres traducir.</p>', unsafe_allow_html=True)

# Display centered image
image = Image.open('OIG7.jpg')
st.image(image, width=300, caption="Traductor", use_column_width='auto')

with st.sidebar:
    st.subheader("Traductor")
    st.write("Presiona el botón, cuando escuches la señal "
             "habla lo que quieres traducir, luego selecciona"
             " la configuración de lenguaje que necesites.")

st.markdown('<p class="paragraph-font">Toca el botón y habla lo que quieres traducir.</p>', unsafe_allow_html=True)

# Button for speech-to-text
stt_button = Button(label="Escuchar 🎤", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Streamlit Bokeh events for handling speech-to-text
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))

    # Create temp folder if not exists
    if not os.path.exists("temp"):
        os.mkdir("temp")

    st.markdown('<p class="title-font">Texto a Audio</p>', unsafe_allow_html=True)
    translator = Translator()

    # Get spoken text and choose input/output languages
    text = str(result.get("GET_TEXT"))
    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        ("Inglés", "Español", "Alemán", "Italiano", "Francés", "Japonés")
    )

    input_language = {
        "Inglés": "en",
        "Español": "es",
        "Alemán": "de",
        "Italiano": "it",
        "Francés": "fr",
        "Japonés": "ja"
    }[in_lang]

    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Alemán", "Coreano", "Mandarín", "Japonés")
    )

    output_language = {
        "Inglés": "en",
        "Español": "es",
        "Alemán": "de",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }[out_lang]

    # Select English accent if applicable
    english_accent = st.selectbox(
        "Selecciona el acento",
        ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica")
    )

    tld = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }[english_accent]

    # Function to translate and convert text to speech
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[:20] if len(text) > 20 else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar el texto")

    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(output_text)

    # Function to remove old files
    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

    remove_files(7)
