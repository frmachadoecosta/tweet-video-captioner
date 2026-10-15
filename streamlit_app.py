import os
from pathlib import Path

import streamlit as st

from src.tweet_to_video import Tweet_Processor


st.set_page_config(page_title="X Post to Video", page_icon="🎬")
st.title("X Post to Video")
st.write("Paste an X/Twitter post URL to download its video with a caption.")

post_url = st.text_area(
    "Post URL",
    placeholder="https://x.com/username/status/1234567890",
    height=80,
)
token = st.text_input(
    "X API bearer token",
    value=os.environ.get("BEARER_TOKEN", ""),
    type="password",
    help="Set BEARER_TOKEN in the environment or paste your token here.",
)

if st.button("Create video", type="primary", disabled=not post_url.strip()):
    if not token.strip():
        st.error("Provide an X API bearer token or set the BEARER_TOKEN environment variable.")
    else:
        try:
            with st.spinner("Downloading the post and creating the video..."):
                output_path = Tweet_Processor(
                    post_url.strip(),
                    bearer_token=token.strip(),
                ).get_video_w_caption()
            st.session_state["processed_video"] = str(output_path)
            st.success("Your video is ready to download.")
        except Exception as error:
            st.exception(error)

video_path_value = st.session_state.get("processed_video")
if video_path_value:
    video_path = Path(video_path_value)
    if video_path.is_file():
        st.video(str(video_path))
        st.download_button(
            "Download video",
            data=video_path.read_bytes(),
            file_name=video_path.name,
            mime="video/mp4",
        )
