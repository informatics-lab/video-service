#!/usr/bin/env python

import argparse as ap
import restnavigator as rn
import tempfile
import urllib
import os
import shutil
import sys
sys.append("./config")
import analysis_config as config

class Job(object):
    def __init__(self, message):
        self.profile = message["profile"]
        self.model = message["model"]
        self.variable = message["variable"]
        self.message = message

    def __str__(self):
        return __dict__

    def __repr__(self):
        return __dict__


def getQueue(queue_name):
    conn = boto.sqs.connect_to_region(os.getenv("AWS_REGION"),
                                      aws_access_key_id=os.getenv("AWS_KEY"),
                                      aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
    queue = conn.get_queue(queue_name)
    return queue


def getJob(queue, visibility_timeout=60):
    messages = queue.get_messages(visibility_timeout, number_messages=1) #get all messages
    try:
        message = messages[0]
    except IndexError:
        raise NoJobsError()

    return Job(message) # NOT YET IMPLIMETNED


if __name__ == "__main__":
    video_service_queue = getQueue("video_service_queue")
    job = getJob(video_service_queue)

    settings = ap.Namespace(**config.profile[job.profile])
    rootnav = rn.Navigator.hal(config.roothal)

    try:
        varnav = rootnav["models"][job.model]["latest"][job.variable]
    except rn.exc.OffTheRailsException:
        raise rn.exc.OffTheRailsException("Variable " + job.variable + "not found."))
    else:
        imgnav = varnav["images"]
        tempdir = tempfile.mkdtemp()
        for thisimgnav in imgnav:
            img = thisimgnav.embedded()["images"]
            imgmetadata = thisimgnav.fetch()
            urllib.urlretrieve(img.uri,
                    os.path.join([tmpdir, imgmetadata['forecast_reference_time']+".png"]))
            with tempfile.SpooledTemporaryFile(max_size=2e7, suffix=settings.video_ending) as vid:
                # wrapping the wildcard in single quotes below means that it is not exanded by the shell
                args = settings.ffmpeg_args_template
                args[args.index("FILES_IN")] = "'"+os.path.join([tmpdir, "*.png"]+"'")
                args[args.index("FILE_OUT")] = vid
                os.call(args)

                payload = imgmetadata.pop("forecast_time")
                r = requests.post(config.vid_dest, data=payload, files={"data": vid})
                if r.status_code != 201:
                    raise IOError(r.status_code, r.text)
        shutil.rmtree(tempdir)

        video_service_queue.delete(job.message)

        sys.exit()