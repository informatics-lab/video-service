#!/usr/bin/env python

import time
import argparse as ap
import config
import restnavigator as rn
import logging
import tempfile
import urllib
import os
import shutil


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler('imageservice.log', maxBytes=1e6, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":
    argparser = ap.ArgumentParser()
    argparser.add_argument("-s", "--settings", default="default",
        type=str, help="Name of analysis settings, as defined in config.py")
    call_args = argparser.parse_args()
    settings = ap.Namespace(**config.settings[call_args["settings"]])

    rootnav = rn.Navigator(config.roothal)

    while True:
        try: # catch all try except so that service keeps running
            for variable in settings.variables:
                try:
                    varnav = rootnav["models"][0][settings.model][0]["latest"][0][variable][0]
                except rn.exc.OffTheRailsException:
                    logger.exception(rn.exc.OffTheRailsException("Variable " + variable + "not found."))
                else:
                    imgnav = varnav["images"]
                    if ("videos" not in varnav.links().keys()) and (len(imgnav) == settings.nframes):
                        logger.info("Making video for " \
                                    + imgnav[0].fetch()["forecast_reference_time"] \
                                    + " " + variable)
                        tempdir = tempfile.mkdtemp()
                        for thisimgnav in imgnav:
                            img = thisimgnav[0].embedded()["images"]
                            imgmetadata = thisimgnav.fetch()
                            urllib.urlretrieve(img.uri,
                                    os.path.join([tmpdir, imgmetadata['forecast_reference_time']+".png"]))
                            with tempfile.SpooledTemporaryFile(max_size=2e7, suffix=settings.video_ending) as vid:
                                # wrapping the wildcard in single quotes below means that it is not exanded by the shell
                                args = settings.ffmpeg_args_template
                                args[args.index("FILES_IN")] = "'"+os.path.join([tmpdir, "*.png"]+"'")
                                args[args.index("FILE_OUT")] = vid
                                logger.info("Calling ffmpeg with these args: ", args)
                                os.call(args)

                                payload = imgmetadata.pop("forecast_time")
                                r = requests.post(config.vid_dest, data=payload, files={"data": vid})
                                if r.status_code != 201:
                                    raise IOError(r.status_code, r.text)
                                logger.info("Video posted")
                        shutil.rmtree(tempdir)
        except BaseException as e:
            logger.exception(e)
        time.sleep(60)