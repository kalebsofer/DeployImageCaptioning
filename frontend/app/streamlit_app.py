import streamlit as st
import requests
import time
from config.settings import get_settings

settings = get_settings()
st.set_page_config(page_title="Simple Image Caption", layout="wide")

st.title("Simple Image Caption")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    if st.button("Submit"):
        placeholder = st.empty()
        start_time = time.time()
        with st.spinner("Processing..."):
            try:
                files = {"file": uploaded_image.getvalue()}
                # Display timer while waiting for response
                while True:
                    elapsed_time = int(time.time() - start_time)
                    placeholder.text(f"Elapsed time: {elapsed_time} seconds")
                    response = requests.post(
                        settings.BACKEND_URL + "/generate-caption",
                        files=files,
                        timeout=3,  # Adjust timeout as needed
                    )
                    if response.status_code == 200:
                        break
                    if response.status_code == 500:
                        raise requests.exceptions.RequestException(
                            "Internal server error"
                        )
                    if response.status_code == 503:
                        raise requests.exceptions.RequestException(
                            "Service unavailable"
                        )
                    if elapsed_time > 20:
                        raise requests.exceptions.Timeout("Request timed out")
                    time.sleep(1)
                result_text = response.text
                placeholder.empty()
                st.subheader("Response:")
                st.write(result_text)
            except requests.exceptions.RequestException as e:
                placeholder.empty()
                st.error(f"Error connecting to backend service: {str(e)}")
