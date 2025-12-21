import shutil
import subprocess
from io import BytesIO
from PIL import Image

def get_frame_from_video(source_path):
	timestamps = ['1', '0']

	for time in timestamps:
		command = [
			"ffmpeg",
			"-i", source_path,
			"-ss", time,
			"-vframes", "1",
			"-f", "image2pipe",
			"-"
		]

		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if result.returncode == 0 and len(result.stdout) > 0:
			return result.stdout
	#gets frame at 1 sec, if video is shorter, gets frame at 0 sec. if neither work return None
	return None


def video_source_generator(source, **kwargs):

	if not source.name.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".webm")):
		return None

	if not shutil.which("ffmpeg"):
		print("WARNING: FFMPEG not installed")
		return None

	try:
		image_data = get_frame_from_video(source.path)
		if image_data:
			return Image.open(BytesIO(image_data))
	except Exception as e:
		print(f"Error generating video thumbnail for {source.name}:\n{e}")

	return None