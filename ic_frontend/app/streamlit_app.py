import streamlit as st
import requests
from config.settings import get_settings

settings = get_settings()

st.set_page_config(page_title="Inventive Image Caption", layout="wide")

st.title("Inventive Image Caption")

if "image_uploaded" not in st.session_state:
    st.session_state.image_uploaded = False

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    st.session_state.image_uploaded = True
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    if st.button("Submit"):
        try:
            files = {"file": uploaded_image.getvalue()}
            response = requests.post(
                f"{settings.BACKEND_URL}/generate-caption",
                files=files,
                timeout=settings.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
            caption = result.get("caption", "No caption generated.")

            st.subheader("Generated Caption:")
            st.write(caption)

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")

else:
    st.write("Upload an image to generate a caption.")
