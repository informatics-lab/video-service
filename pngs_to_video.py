import subprocess as sp

def imgs_to_video(file_naming, file_out, fps=20):
	"""
	Converts images to video using FFMPEG

	Args:
	    * file_naming (str):
	    as per argument in FFMPEG i.e. the general file name using
	    c-style string substitution. E.g. name%03d.png would include name001.png,
	    name002.png etc

	    * file_out (str):
	    name of the file to write to

	    * fps (int):
	    frames per second
	"""
	if file_out.endswith(".ogv"):
		codec = "libtheora"

	sp.call(["ffmpeg", "-r", fps, "-i", file_naming, "-c:v", codec, file_out])