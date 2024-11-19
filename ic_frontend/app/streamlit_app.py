import streamlit as st
import requests
import uuid
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

    image_id = str(uuid.uuid4())

    if st.button("Submit"):
        try:
            files = {"file": uploaded_image.getvalue()}
            data = {"image_id": image_id}
            response = requests.post(
                f"{settings.BACKEND_URL}/generate-caption",
                files=files,
                data=data,
                timeout=settings.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
            caption = result.get("caption", "No caption generated.")

            st.subheader("Generated Caption:")
            st.write(caption)

            st.subheader("Provide Feedback")
            score = st.slider("Rate the caption (1-10)", 1, 10, 5)
            user_caption = st.text_input("Your caption")

            if st.button("Submit Feedback"):
                feedback_data = {
                    "score": score,
                    "user_caption": user_caption,
                    "generated_caption": caption,
                    "image_name": uploaded_image.name,
                    "image_id": image_id,
                }
                st.success("Thank you for your feedback!")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")

else:
    st.write("Upload an image to generate a caption.")
