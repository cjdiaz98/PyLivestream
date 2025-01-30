import subprocess
import re
import sys
import os

def parse_mylist_txt(mylist_path):
	"""
	Read mylist.txt and extract file paths of the form:
	file 'C:/path/to/video.mp4'
	Returns a list of actual file paths (strings).
	"""
	file_paths = []
	with open(mylist_path, 'r', encoding='utf-8') as f:
		for line in f:
			line = line.strip()
			if line.startswith("file '") and line.endswith("'"):
				# Example line: file 'C:/path/to/video.mp4'
				# Extract the path between the quotes.
				match = re.match(r"^file '(.+)'$", line, re.IGNORECASE)
				if match:
					file_path = match.group(1)
					file_paths.append(file_path)
	return file_paths

def get_media_info(filepath):
	"""
	Use ffprobe to extract key video/audio information for the given file.
	
	Returns a dict, for example:
	{
	   'video_codec': 'h264',
	   'width': 1920,
	   'height': 1080,
	   'fps': '30000/1001'   # or '30/1' or similar
	   'audio_codec': 'aac',
	   'sample_rate': 48000,
	   'channels': 2
	}
	If a stream is missing (e.g. no audio), the corresponding fields may be None.
	"""
	
	# ffprobe commands to get video info
	# - show_entries for video stream: 'codec_name,width,height,avg_frame_rate'
	# - show_entries for audio stream: 'codec_name,sample_rate,channels'
	cmd_video = [
		"ffprobe",
		"-v", "error",
		"-select_streams", "v:0",
		"-show_entries", "stream=codec_name,width,height,avg_frame_rate",
		"-of", "default=noprint_wrappers=1:nokey=1",
		filepath
	]
	
	cmd_audio = [
		"ffprobe",
		"-v", "error",
		"-select_streams", "a:0",
		"-show_entries", "stream=codec_name,sample_rate,channels",
		"-of", "default=noprint_wrappers=1:nokey=1",
		filepath
	]
	
	# Run ffprobe for video
	try:
		video_out = subprocess.check_output(cmd_video, stderr=subprocess.STDOUT)
		video_lines = video_out.decode("utf-8", errors="replace").splitlines()
		# Expecting up to 4 lines: codec, width, height, avg_frame_rate
		if len(video_lines) >= 4:
			video_codec, width, height, fps = video_lines[:4]
		else:
			# Might be no video track at all
			video_codec, width, height, fps = (None, None, None, None)
	except subprocess.CalledProcessError:
		# Means no video or an error
		video_codec, width, height, fps = (None, None, None, None)
	
	# Run ffprobe for audio
	try:
		audio_out = subprocess.check_output(cmd_audio, stderr=subprocess.STDOUT)
		audio_lines = audio_out.decode("utf-8", errors="replace").splitlines()
		# Expecting up to 3 lines: codec, sample_rate, channels
		if len(audio_lines) >= 3:
			audio_codec, sample_rate, channels = audio_lines[:3]
		else:
			# Might be no audio track
			audio_codec, sample_rate, channels = (None, None, None)
	except subprocess.CalledProcessError:
		# Means no audio or an error
		audio_codec, sample_rate, channels = (None, None, None)
	
	# Convert width/height/sample_rate/channels to ints if possible
	def to_int(val):
		try:
			return int(val)
		except (ValueError, TypeError):
			return None
	
	info = {
		'video_codec': video_codec,
		'width': to_int(width),
		'height': to_int(height),
		'fps': fps,  # We'll keep the raw fraction string e.g. '30/1'
		'audio_codec': audio_codec,
		'sample_rate': to_int(sample_rate),
		'channels': to_int(channels),
	}
	
	return info

def check_compatibility(file_info_list):
	"""
	Check that all dictionaries in file_info_list have the same
	key values for the relevant parameters (video_codec, resolution, fps, audio_codec, etc.).
	
	Raises ValueError if there's a mismatch. If everything matches, just returns None.
	"""
	if not file_info_list:
		raise ValueError("No files to compare")
	
	# Reference info is the first file's properties
	ref = file_info_list[0]
	print(f"Reference file: {ref}")
	
	for idx, info in enumerate(file_info_list[1:], start=2):
		# Compare to reference
		mismatches = []
		
		# Check video codec
		if info['video_codec'] != ref['video_codec']:
			mismatches.append(f"video_codec: {info['video_codec']} != {ref['video_codec']}")
		
		# Check width/height
		if info['width'] != ref['width'] or info['height'] != ref['height']:
			mismatches.append(f"resolution: {info['width']}x{info['height']} != {ref['width']}x{ref['height']}")
		
		# Check frame rate
		if info['fps'] != ref['fps']:
			mismatches.append(f"fps: {info['fps']} != {ref['fps']}")
		
		# Check audio codec
		if info['audio_codec'] != ref['audio_codec']:
			mismatches.append(f"audio_codec: {info['audio_codec']} != {ref['audio_codec']}")
		
		# Check sample rate
		if info['sample_rate'] != ref['sample_rate']:
			mismatches.append(f"sample_rate: {info['sample_rate']} != {ref['sample_rate']}")
		
		# Check channels
		if info['channels'] != ref['channels']:
			mismatches.append(f"channels: {info['channels']} != {ref['channels']}")
		
		if mismatches:
			raise ValueError(
				f"File #{idx} does not match reference (File #1) in these fields:\n"
				+ "\n".join(mismatches)
			)

def main(mylist_path):
	# 1. Parse the file paths from mylist.txt
	file_paths = parse_mylist_txt(mylist_path)
	if not file_paths:
		print("No file paths found in mylist.txt.")
		sys.exit(1)
	
	# 2. Collect media info for each file
	file_info_list = []
	for fp in file_paths:
		if not os.path.isfile(fp):
			print(f"Warning: file does not exist: {fp}")
			continue
		
		info = get_media_info(fp)
		file_info_list.append(info)
	
	print("Reference file: ", file_paths[0])
	# Check we have any valid files
	if not file_info_list:
		print("No valid files to analyze.")
		sys.exit(1)
	
	# 3. Check for compatibility
	try:
		check_compatibility(file_info_list)
		print("All listed files are compatible for concatenation!")
	except ValueError as e:
		print("Incompatible files detected:")
		print(str(e))
		sys.exit(2)

if __name__ == "__main__":
	# Provide a default, or pass in from the command line
	# e.g. `python check_compat.py mylist.txt`
	if len(sys.argv) < 2:
		print(f"Usage: python {sys.argv[0]} mylist.txt")
		sys.exit(1)
	
	mylist_path = sys.argv[1]
	main(mylist_path)
	# info = get_media_info("C:/Users/cjdia/Downloads/kling/snake.mp4")
	# print(info)
