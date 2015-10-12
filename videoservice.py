#!/usr/bin/env python

import argparse as ap
import restnavigator as rn
import tempfile
import urllib
import os
import shutil
import sys
import boto
import boto.sqs
import json
import time
import requests

sys.path.append(".")
from config import analysis_config as conf

class Job(object):
    def __init__(self, message):
        body = json.loads(message.get_body())
        self.profile_name = body["profile_name"]
        self.model = body["model"]
        self.variable = body["variable"]
        self.nframes = body["nframes"]
        self.message = message

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


def getQueue(queue_name):
    conn = boto.sqs.connect_to_region(os.getenv("AWS_REGION"),
                                      aws_access_key_id=os.getenv("AWS_KEY"),
                                      aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
    queue = conn.get_queue(queue_name)
    return queue


class NoJobsError(Exception):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return repr(self.value)


def getJob(queue, visibility_timeout=1*60):
    messages = queue.get_messages(1, visibility_timeout=visibility_timeout)

    try:
        message = messages[0]
    except IndexError:
        raise NoJobsError()

    return Job(message) # NOT YET IMPLIMETNED


if __name__ == "__main__":
    print "Getting job"
    video_service_queue = getQueue("video_service_queue")
    job = getJob(video_service_queue)
    print job

    settings = ap.Namespace(**conf.profiles[job.profile_name])
    rootnav = rn.Navigator.hal(conf.roothal)

    try:
        varnav = rootnav["models"][job.model]["latest"][job.variable]
    except rn.exc.OffTheRailsException:
        print "Variable doesn't exist for job, " + job + " sleeping"
        time.sleep(int(os.getenv("RETRY_TIME")))
        raise rn.exc.OffTheRailsException("Variable " + job.variable + "not found.")
    else:
        imgs = varnav[job.profile_name]["images"].embedded()["images"]
        if len(imgs) < job.nframes: 
            print "Not enough timesteps, sleeping..."
            time.sleep(int(os.getenv("RETRY_TIME")))
            raise IOError("Only " + str(len(imgs)) + " of " + str(job.nframes) + " found, sleeping...")
        tempdir = tempfile.mkdtemp()
        print "Getting images"
        for i, img in enumerate(imgs):
            print "Doing image ", img
            imgmetadata = img.fetch()
            urllib.urlretrieve(img.links()["data"].uri,
                    os.path.join(tempdir, imgmetadata['forecast_time'] + ".png"))

        for i, file in enumerate(sorted(os.listdir(tempdir))):
            print "Renaming " + file + " to file%03d.png" % i
            os.rename(os.path.join(tempdir, file), os.path.join(tempdir, "file%03d.png" % i))

        tempfilep = os.path.join(tempfile.gettempdir(), "temp."+settings.video_ending)
        with open(tempfilep, "wb") as vid:
            args = settings.ffmpeg_args_template
            args[args.index("FILES_IN")] = os.path.join(tempdir, "file%03d.png")
            args[args.index("FILE_OUT")] = vid.name
            print args
            success = os.system(' '.join(args))
            if success != 0:
                raise Exception("ffmpeg failed with return code " + str(success))  

        with open(tempfilep, "rb") as vid:
            payload = imgmetadata
            payload["forecast_time"] = imgmetadata.pop("forecast_time")
            payload["mime_type"] = "video/ogg"
            payload["resolution_x"] = imgmetadata["resolution"]["x"]
            payload["resolution_y"] = imgmetadata["resolution"]["y"]
            payload.pop("resolution")
            payload["data_dimension_x"] = imgmetadata["data_dimensions"]["x"]
            payload["data_dimension_y"] = imgmetadata["data_dimensions"]["y"]
            payload["data_dimension_z"] = imgmetadata["data_dimensions"]["z"]
            payload.pop("data_dimensions")
            payload["geographic_region"] = json.dumps(imgmetadata["geographic_region"])
            print payload
            r = requests.post(conf.vid_data_server, data=payload, files={"data": vid})
            if r.status_code != 201:
                raise IOError(r.status_code, r.text)
            else:
                print r.headers
                print "Posted video to data service"
        print "Removing tempdirectory", tempdir
        shutil.rmtree(tempdir)

        print "Removing completed"
        video_service_queue.delete_message(job.message)

        sys.exit()