roothal = "http://ec2-52-16-246-202.eu-west-1.compute.amazonaws.com:9000/molab-3dwx-ds/"
vid_dest = "http://ec2-52-16-246-202.eu-west-1.compute.amazonaws.com:9000/molab-3dwx-ds/media/"

settings = {
	"default": {"model": "ukv",
			"variables": ["cloud_fraction_in_a_layer"],
			"nframes": 35,
			"video_ending": "ogv",
			"ffmpeg_args_template": ["ffmpeg", "-r", "20", "-i", "FILES_IN",
									 "-r", "20", "-c:v", "libtheora", "FILE_OUT"]
			},
	"ukv": {"model": "ukv",
			"variables": ["cloud_fraction_in_a_layer"],
			"nframes": 35,
			"video_ending": "ogv",
			"ffmpeg_args_template": ["ffmpeg", "-r", "20", "-i", "FILES_IN",
									 "-r", "20", "-c:v", "libtheora", "FILE_OUT"]
			}
}