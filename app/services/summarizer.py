from app.models.gemini import Model as GeminiModel
import os
import yt_dlp
import re
import tempfile
import shutil
from datetime import datetime

class Summarizer:
    """Summarizes a YouTube podcast"""

    def __init__(self):
        self.model = GeminiModel()
        self.temp_dir = tempfile.mkdtemp()  # Create a temporary directory


    def __del__(self):
        # Clean up the temporary directory when the object is destroyed
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by replacing invalid characters."""
        return re.sub(r'[\/:*?"<>|]', '_', filename)  # Replace invalid characters with '_'


    def download_audio(self, url: str) -> str:
        """Download the highest quality audio stream from a YouTube URL and return the file path."""
        
        # # Use app directory-based path
        # app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # download_path = os.path.join(app_dir, 'data')

        # Extract video info first to modify the title
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                raise RuntimeError(f"Failed to fetch video info: {e}")

        title = self.sanitize_filename(info.get("title", "unknown").replace(" ", "_"))  # Replace spaces with underscores
        ext = "mp3"

        # # Construct the full output path
        # output_template = os.path.join(download_path, f"{title}.%(ext)s")
        # final_audio_path = os.path.join(download_path, f"{title}.{ext}")

        # Use temporary directory
        output_template = os.path.join(self.temp_dir, f"{title}.%(ext)s")
        final_audio_path = os.path.join(self.temp_dir, f"{title}.{ext}")

        ydl_opts = {
            'format': 'bestaudio/best',         # Choose the best audio format available
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',    # Convert audio to a specific format
                'preferredcodec': ext,          # You can change the codec to 'aac', 'ogg', 'wav', etc.
                'preferredquality': '192',      # Set the audio quality (e.g., 192kbps)
            }],
            'outtmpl': output_template,         # Output path and naming convention (or downloads/%(title)s.%(ext)s)
            'quiet': False,                     # Set to True for less output during download
        }
        
        # # Ensure the download path exists
        # os.makedirs(download_path, exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            if duration > 7200: # 2 hours in seconds
                raise ValueError(f"Video duration too long: {duration}")
            
            try:
                ydl.download([url])
            except Exception as e:
                raise RuntimeError(f"Download failed: {e}")
        
        # Return the final path of the downloaded audio file
        return final_audio_path
    

    def get_video_info(self, url: str) -> dict:
        """Get basic video information without downloading."""
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title", "Unknown"),
                    "channel": info.get("channel", "Unknown"),
                    "duration": info.get("duration", 0),
                    "description": info.get("description", ""),
                    "publish_date": info.get("upload_date", datetime.now().date().isoformat()),
                    "url": url
                }
            except Exception as e:
                raise RuntimeError(f"Failed to fetch video info: {e}")


    def get_speaker_interviewee_name(self, yt_description: str) -> str:
        prompt = f"""
        Extract the full name of the speaker or interviewee from the following YouTube description.

        The name might appear early in the description, possibly following phrases like:
        - "interview with"
        - "conversation with"
        - "chatting with"
        - "speaking with"
        - "a talk with"
        - "talking to"
        - "joined by"
        - "featuring"
        - "with special guest"
        - or, in the case of a solo podcast, they may simply be introduced as the host or the person presenting the topic.

        Please format the name in the 'First Last' format (e.g., 'John Doe'), even if the description presents it differently (e.g., 'Doe, John'). 

        If a full name is not available, return the most complete identifier that refers to the speaker or interviewee (e.g., first name, handle, or username). Prioritize real full names when possible.

        It is **important that you only return the name of the speaker or interviewee, and no additional information**.

        Description:
        {yt_description}
        """
        res = self.model.get_response(prompt)
        return res.strip()


    def format_duration(self, seconds: int) -> str:
        """Format duration in seconds to hours and minutes."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"


    def generate_filename(self, video_info: dict) -> str:
        date = video_info.get("publish_date")
        channel = video_info.get("channel").replace(" ", "")
        # title = self.sanitize_filename(video_info.get("title", "Untitled")).replace(" ", "_")
        speaker_interviewee = self.get_speaker_interviewee_name(video_info.get("description")).replace(" ", "")

        # # Trim long titles and ensure filename is not too long
        # max_title_length = 25
        # if len(title) > max_title_length:
        #     title = title[:max_title_length] + "_truncated"

        filename = f"{date}-{speaker_interviewee}-{channel}"
        return filename


    def generate_markdown_file(self, title: str, channel: str, publish_date: str, duration: int, insights: str, url: str, slug: str) -> None:
        markdown_content = f"""---
title: "{title}"
channel: "{channel}"
published: "{publish_date}"
duration: "{self.format_duration(duration)}"
---

{insights}

---

<a href="{url}" target="_blank">Check out the full episode on YouTube!</a>
        """

        base_dir = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of the current script
        posts_dir = os.path.join(base_dir, "..", "..", "posts") # Goes up two directories, then to "posts"
        file_path = os.path.join(posts_dir, f"{slug}.md")
        os.makedirs(posts_dir, exist_ok=True) # Ensure the directory exists

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(markdown_content)


    def get_summary(self, url: str) -> dict:
        """Download a YouTube video's audio and generate a summary."""
        try:
            # Get video info
            video_info = self.get_video_info(url)

            # Check duration
            if video_info["duration"] > 7200:  # 2 hours
                raise ValueError("Video duration too long. Maximum duration is 2 hours.")

            # Download audio
            audio_path = self.download_audio(url)

            # Generate summary
            prompt = f"""
            Given this audio file, write an engaging blog article about this podcast. The blog article should:

            - Use a single '#' for the main title (H1 heading)
                * Create a title that captures the essence of the podcast
                * DO NOT use generic terms like "summary," "review," or "overview" in the title
            - Include a brief introduction (2-3 sentences) that gives context about the podcast and its host/guests. Refer to the podcast's description for more context but DO NOT copy from it directly:
                - {video_info.get("description")}
            - Present 3-5 valuable insights from the podcast as distinct sections with descriptive headings (avoid numbering the headings)
            - Incorporate 2-3 notable direct quotes from the podcast
            - End with a brief conclusion that captures the overall value or takeaway 
            - Add a "Who Is This For?" recommendation section at the very end, using bullet points, that clearly identifies:
                * Target audience (keep it concise)
                * Why it is worth listening to (highlight unique insights, practical tools, or perspective shifts that make it valuable)

            IMPORTANT FORMATTING RULES:
            1. The ENTIRE article must be between 400-600 words total
            2. Use proper Markdown syntax. Examples:
                - Headings: # Main Title, ## Section Heading, and so on
                - Emphasis: **bold text**, *italic text*
                - Blockquotes for podcast quotes: > "Quote goes here" — Speaker Name
                    - Always place quotes on their own line
                - Lists: * Item or - Item
            3. DO NOT wrap the response in markdown code blocks (```)

            Write in a conversational yet intelligent tone that feels like a blog post rather than a summary document. Focus on making the article engaging and valuable to readers who want to quickly understand if this podcast is worth their time.
            """

            summary = self.model.execute_prompt_from_audio(prompt, audio_path)

            # Clean up - delete the audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

            # Generate markdown file
            slug = self.generate_filename(video_info)
            self.generate_markdown_file(video_info.get("title"), video_info.get("channel"), video_info.get("publish_date"), video_info.get("duration"), summary, video_info.get("url"), slug)

            return {
                "video_info": video_info,
                "summary": summary
            }

        except Exception as e:
            raise RuntimeError(f"Error summarizing the podcast: {str(e)}")
