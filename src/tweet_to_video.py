"""
Main class to handle url requests and return video w/ caption
"""
import requests
import os
import json
import re
import urllib.request
import numpy as np
from pathlib import Path

from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

if __package__:
    from .manipulate_video import create_header
else:
    from manipulate_video import create_header

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

class Tweet_Processor():
    def __init__(self, request_url, bearer_token=None):
        self.request_url = request_url
        self.id = self._get_tweet_id()
        self.api_url = f"https://api.x.com/2/tweets/{self.id}"
        self.bearer_token = bearer_token or BEARER_TOKEN
        if not self.bearer_token:
            raise ValueError("Set the BEARER_TOKEN environment variable or pass a bearer token.")

    def _get_tweet_id(self):
        """
        gets tweet_id from url
        """
        return self.request_url.split("/")[-1]

    @staticmethod
    def _request_url_response(url, json_name, bearer_token):
        """
        requests tweet info via API and caches in json format
        """
        params = {
            "expansions": "attachments.media_keys",
            "tweet.fields": "text",
            "media.fields": "type,variants,preview_image_url"
        }
        headers = {"Authorization": f"Bearer {bearer_token}"}

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        print("Status:", resp.status_code)
        data = resp.json()

        caption = data["data"]["text"]
        quoted_caption = re.search(r'"([^"]+)"|“([^”]+)”', caption, re.DOTALL)
        if quoted_caption:
            caption = next(group for group in quoted_caption.groups() if group is not None)
        else:
            caption = re.sub(r"https?://\S+", "", caption)
        caption = " ".join(caption.split())

        print("Caption:", caption)

        os.makedirs("cache/json", exist_ok=True)
        with open(f"cache/json/{json_name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return data, caption

    def _get_media(self, work_json):
        """
        downloads video from json with appropriate format
        """

        media_items = work_json.get("includes", {}).get("media", [])
        video = next((item for item in media_items if item.get("type") == "video"), None)
        if video is None:
            raise ValueError("The post does not contain a video.")

        variants = [
            variant
            for variant in video.get("variants", [])
            if variant.get("content_type") == "video/mp4" and variant.get("url")
        ]
        if not variants:
            raise ValueError("The post does not contain a downloadable MP4 video.")
        best_variant = max(variants, key=lambda variant: variant.get("bit_rate", 0))
        work_url = best_variant["url"]

        os.makedirs("cache/video", exist_ok=True)
        path = f"cache/video/{self.id}.mp4"
        urllib.request.urlretrieve(work_url, path)
        return path

    def _create_video_w_caption(self, video_path_w_extension, caption):
        """
        Creates captioned video from cached file
        """
        output_path = f"cache/output/{self.id}_worked.mp4"
        os.makedirs("cache/output", exist_ok=True)

        video = VideoFileClip(video_path_w_extension)

        font_candidates = [
            Path(os.environ["VIDEO_FONT_PATH"]) if os.environ.get("VIDEO_FONT_PATH") else None,
            Path(__file__).resolve().parent.parent / "assets" / "arialbd.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ]
        font_path = next(
            (str(path) for path in font_candidates if path is not None and path.is_file()),
            None,
        )


        header_image, header_height = create_header(
            text=caption,
            video_width=video.w,
            font_path=font_path,
            max_font_size=90,
        )


        # Convert PIL image to MoviePy clip
        header = ImageClip(
            np.array(header_image)
            ).with_duration(video.duration
                            )

        # Put video underneath the header
        video_positioned = video.with_position(
            (0, header_height)
        )

        # Explicitly define the FULL canvas size
        final_width = video.w
        final_height = header_height + video.h

        result = CompositeVideoClip(
            [
                header,
                video_positioned,
            ],
            size=(final_width, final_height)
        )

        result.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
                ffmpeg_params=[
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart"
            ],
        )
        result.close()
        video.close()
        return output_path

    def get_video_w_caption(self):
        """
        main function to generate the video w/ caption
        from tweet url
        """
        tweet_json, caption = self._request_url_response(
            self.api_url,
            self.id,
            self.bearer_token,
        )
        stored_video_path = self._get_media(tweet_json)

        return self._create_video_w_caption(stored_video_path, caption)

if __name__ == "__main__":
    t = Tweet_Processor("https://x.com/memechaotic/status/2110415587205673408")
    t.get_video_w_caption()
