import streamlit as st
import requests
import uuid
from config.settings import get_settings
from logs import log_manager

settings = get_settings()

st.set_page_config(page_title="Inventive Image Caption", layout="wide")

st.title("Inventive Image Caption")

# Initialize session state variables
if "image_uploaded" not in st.session_state:
    st.session_state.image_uploaded = False
if "caption" not in st.session_state:
    st.session_state.caption = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False


def reset_state():
    st.session_state.image_uploaded = False
    st.session_state.caption = None
    st.session_state.feedback_submitted = False


uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None and not st.session_state.image_uploaded:
    st.session_state.image_uploaded = True
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    image_id = str(uuid.uuid4())
    user_id = log_manager.get_or_create_user_id()
    session_id = log_manager.get_or_create_session_id()

    if st.button("Submit"):
        try:
            files = {"file": uploaded_image.getvalue()}
            data = {"image_id": image_id, "temperature": 1.0}
            response = requests.post(
                f"{settings.BACKEND_URL}/generate-caption",
                files=files,
                data=data,
                timeout=settings.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
            st.session_state.caption = result.get("caption", "No caption generated.")

            log_manager.log_caption(
                image_id=image_id,
                generated_caption=st.session_state.caption,
                feedback_received=False,
                rating=None,
                ideal_caption=None,
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")

if st.session_state.caption:
    st.subheader("Generated Caption:")
    st.write(st.session_state.caption)

    if not st.session_state.feedback_submitted:
        st.subheader("Provide Feedback")
        score = st.slider("Rate the caption (1-10)", 1, 10, 5)
        user_caption = st.text_input("Please provide accurate caption")

        if st.button("Submit Feedback"):
            log_manager.log_caption(
                image_id=image_id,
                generated_caption=st.session_state.caption,
                feedback_received=True,
                rating=score,
                ideal_caption=user_caption,
            )
            st.success("Thank you for your feedback!")
            st.session_state.feedback_submitted = True

if st.session_state.feedback_submitted:
    if st.button("Upload Another Image"):
        reset_state()
