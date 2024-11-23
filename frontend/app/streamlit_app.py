import streamlit as st
import requests
import time
from config.settings import get_settings
from logs import log_manager
import uuid

settings = get_settings()

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

st.set_page_config(page_title="Simple Image Caption", layout="wide")

st.title("Simple Image Caption")
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

col1,col2 = st.columns(2)


if uploaded_image is not None:
    st.session_state.image_uploaded = True
    with col1:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    image_id = str(uuid.uuid4())
    user_id = log_manager.get_or_create_user_id()
    session_id = log_manager.get_or_create_session_id()

    with col2:
        temperature = st.slider("Temperature", min_value=0.05, max_value=2.0, value=0.5, step=0.05)
        if st.button("Submit"):
            placeholder = st.empty()
            start_time = time.time()
            with st.spinner("Processing..."):
                try:
                    files = {"file": uploaded_image.getvalue()}
                    data = {"image_id": 'aaa', "temperature": 1.0}
                    # Display timer while waiting for response
                    while True:
                        elapsed_time = int(time.time() - start_time)
                        # placeholder.text(f"Elapsed time: {elapsed_time} seconds")
                        response = requests.post(
                            f"{settings.BACKEND_URL}/generate-caption",
                            files=files,
                            data=data,
                            timeout=settings.TIMEOUT_SECONDS,
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
                        if elapsed_time > 60:
                            raise requests.exceptions.Timeout("Request timed out")
                        time.sleep(1)
                    result = response.json()
                    st.session_state.caption = result.get("caption", "No caption generated.")
                    placeholder.empty()

                    # log_manager.log_caption(
                    #     image_id=image_id,
                    #     generated_caption=st.session_state.caption,
                    #     feedback_received=False,
                    #     rating=None,
                    #     ideal_caption=None,
                    # )
                except requests.exceptions.RequestException as e:
                    placeholder.empty()
                    st.error(f"Error connecting to backend service: {str(e)}")

        if st.session_state.caption:
            st.subheader("Generated Caption:")
            st.subheader("Response:")
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
                    st.session_state.feedback_submitted = True
                    st.success("Feedback submitted successfully")

        if st.session_state.feedback_submitted:
            if st.button("Upload Another Image"):
                reset_state()