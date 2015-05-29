import request
import shutil
import subprocess as sp
import tempfile

IMAGE_SOURCE = "http://ec2-52-16-246-202.eu-west-1.compute.amazonaws.com:9000/molab-3dwx-ds/images/"
VIDEO_DEST = "http://ec2-52-16-246-202.eu-west-1.compute.amazonaws.com:9000/molab-3dwx-ds/videos/"


def get_images(meta_data, temp_dir):
	"""
	Sends get request to the data service based on a dictionary of meta_data
	and saves returned image files to temp_dir

	"""
	r = request.get(IMAGE_SOURCE, data=meta_data, stream=True)
	with open(temp_dir+"frame%04d.png"%i, 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)


def imgs_to_video(file_naming, file_out):
	"""
	Converts images to video using FFMPEG

	Args:
	    * file_naming (str):
	    as per argument in FFMPEG i.e. the general file name using
	    c-style string substitution. E.g. name%03d.png would include name001.png,
	    name002.png etc

	    * file_out:
	"""

	sp.call(["ffmpeg",  "-y", "-i", source, "-c:v", "libvpx-vp9", "-pass", "1", "-b:v", "1000K",
			"-threads", "8", "-speed", "4", "-tile-columns", "6", "-frame-parallel", "1",
			"-auto-alt-ref", "1", "-lag-in-frames", "25", "-an", "-f", "webm", "/dev/null"])

	sp.call(["ffmpeg", "-y", "-i", source, "-c:v", "libvpx-vp9", "-pass", "2", "-b:v", "1000K",
			"-threads", "8", "-speed", "1", "-tile-columns", "6", "-frame-parallel" "1",
			"-auto-alt-ref", "1", "-lag-in-frames", "25", "-c:a", "libopus", "-b:a", "64k", 
			"-f", "webm", file_out])


def get_meta_data_post(meta_data_get):
	""" Returns the meta data needed for the video post """
	meta_data_get.pop("time")
	return meta_data_get


def make_video(meta_data_get, video_suffix="webm"):
	"""
	Gets video frame images from the image service and encodes them
	as a video, before posting the video back to the data service.
	Args:
		* meta_dat_get (dict): dictionary of metadata for the get request
		* video_suffix (str): ending of the video file
	"""

	temp_dir = tempfile.mkdtemp()
	temp_video = tempfile.mkstemp(suffix=video_suffix)

	try:
		get_images(meta_data_get, temp_dir)
		imgs_to_video(temp_dir+"frame%04d.png", temp_video)
		
		payload = get_meta_data_post(meta_data_get)
		payload['data'] = temp_video

		r = request.post(VIDEO_DEST, payload)
	finally:
		shutil.rmtree(temp_dir)
		shutil.rm(temp_video)