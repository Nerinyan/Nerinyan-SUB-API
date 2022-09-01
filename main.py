import os
import zipfile
import requests
import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse

from common import glob
from modules import config

glob.BASEROOT = pathlib.Path(__file__).parent
config.CONFIG_LOADER()
app = FastAPI()
NERINYAN_API = "https://api.nerinyan.moe"

@app.get("/")
async def root():
    return {"msg": "oh, hi!! (>///<)"}

@app.get("/d/{bid}")
async def download_beatmapset(bid, noVideo: bool = 0, noBg: bool = 0, noHitsound: bool = 0, noStoryboard: bool = 0, nv: bool = 0, nb: bool = 0, nh: bool = 0, nsb: bool = 0):
    noVideo = noVideo | nv
    noBg = noBg | nb
    noHitsound = noHitsound | nh
    noStoryboard = noStoryboard | nsb

    print(f"=====================\nRequest Beatmapset ID: {bid}\nNo Video: {noVideo}\nNo BG: {noBg}\nNo Hitsound: {noHitsound}\nNo Storyboard: {noStoryboard}\n==================")
    
    def checkfile():
        if not os.path.isfile(f"{glob.ROOT_BEATMAP}/{bid}.osz"):
            with requests.get(f"{NERINYAN_API}/d/{bid}", stream=True) as req:
                req.raise_for_status()
                with open (f"{glob.ROOT_UNZIP}/{bid}.osz", 'wb') as f:
                    for chunk in req.iter_content(chunk_size=8192):
                        f.write(chunk)
            unzipfile(istemp=True)


    def unzipfile(istemp: bool = 0):
        if not istemp:
            with zipfile.ZipFile(f"{glob.ROOT_BEATMAP}/{bid}.osz", 'r') as beatmap_ref:
                beatmap_ref.extractall(f"{glob.ROOT_UNZIP}/{bid}")
        else:
            with zipfile.ZipFile(f"{glob.ROOT_UNZIP}/{bid}.osz", 'r') as beatmap_ref:
                beatmap_ref.extractall(f"{glob.ROOT_UNZIP}/{bid}")

    def rebuildBeatmapset(filename):
        hitsounds = ['normal-', 'nightcore-', 'drum-', 'soft-', 'spinnerspin']

        # check if exist re-builded beatmapset output folder
        if not os.path.isdir(f"{glob.ROOT_REBUILD}/{bid}"):
            os.mkdir(f"{glob.ROOT_REBUILD}/{bid}")
            os.mkdir(f"{glob.ROOT_REBUILD}/{bid}/novideo")
        # check if exist already re-builed beatmapset
        if not os.path.isfile(f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}{filename}.osz"):
            with zipfile.ZipFile(f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}{filename}.osz", "w") as rebuild_ref:
                # backup now cwd
                owd = os.getcwd()
                # change cwd to unzipped root
                os.chdir(f"{glob.ROOT_UNZIP}/{bid}/")
                for f in os.listdir('./'):
                    # No BG, No Hitsound AND No Storyboard
                    if noBg and noHitsound and noStoryboard:
                        if noVideo:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not any(x in f for x in hitsounds) and not f.endswith('.osb') and not f == "sb" and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not any(x in f for x in hitsounds) and not f.endswith('.osb') and not f == "sb":
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    # No BG AND No Hitsound
                    elif noBg and noHitsound and not noStoryboard:
                        if noVideo:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not any(x in f for x in hitsounds) and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not any(x in f for x in hitsounds):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    # No BG AND No Storyboard
                    elif noBg and noStoryboard and not noHitsound:
                        if noVideo:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not f.endswith('.osb') and not f == "sb" and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not f.endswith('.osb') and not f == "sb":
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    # No Hitsound AND No Storyboard
                    elif noHitsound and noStoryboard and not noBg:
                        if noVideo:
                            if not any(x in f for x in hitsounds) and not f.endswith('.osb') and not f == "sb" and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not any(x in f for x in hitsounds) and not f.endswith('.osb') and not f == "sb":
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    # No BG
                    elif noBg and not noHitsound and not noStoryboard:
                        if noVideo:
                            if not f.endswith('.png') and not f.endswith('.jpg') and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not f.endswith('.png') and not f.endswith('.jpg'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    # No Hitsound
                    elif noHitsound and not noBg and not noStoryboard:
                        if noVideo:
                            if not any(x in f for x in hitsounds) and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not any(x in f for x in hitsounds):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    # No Storyboard
                    elif noStoryboard and not noBg and not noStoryboard:
                        if noVideo:
                            if not f.endswith('.osb') and not f == "sb" and not f.endswith('.mp4') and not f.endswith('.m4v'):
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                        else:
                            if not f.endswith('.osb') and not f == "sb":
                                # add file to zip
                                rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                # return to default cwd
                os.chdir(owd)

    # get rebuiled file root
    def get_file_root():
        if noBg and noHitsound and noStoryboard:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}all.osz"
        elif noBg and noHitsound and not noStoryboard:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}nobg&nohitsound.osz"
        elif noBg and noStoryboard and not noHitsound:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}nobg&nostoryboard.osz"
        elif noHitsound and noStoryboard and not noBg:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}nohitsound&nostoryboard.osz"
        elif noBg:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}nobg.osz"
        elif noHitsound:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}noHitsound.osz"
        elif noHitsound:
            return f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}nostoryboard.osz"

    def generate_file_name():
        r = requests.get(f"{NERINYAN_API}/search?q={bid}")
        if r.status_code == 200:
            rbody = r.json()[0]
            r.close()
            if noBg and noHitsound and noStoryboard:
                FILETYPE = "[NoBG & NoHitsound & NoStoryboard]"
            elif noBg and noHitsound and not noStoryboard:
                FILETYPE = "[NoBG & NoHitsound]"
            elif noBg and noStoryboard and not noHitsound:
                FILETYPE = "[NoBG & NoStoryboard]"
            elif noHitsound and noStoryboard and not noBg:
                FILETYPE = "[NoHitsound & NoStoryboard]"
            elif noBg and not noHitsound and not noStoryboard:
                FILETYPE = "[NoBG]"
            elif noHitsound and not noBg and not noStoryboard:
                FILETYPE = "[NoHitsound]"
            elif noStoryboard and not noHitsound and not noBg:
                FILETYPE = "[NoStoryboard]"
            return f"{FILETYPE} {bid} {rbody['artist_unicode']} - {rbody['title_unicode']}.osz"


    # beatmap file exist check
    checkfile()
    
    # If requested beatmapset is not unziped then unzip beatmapset
    if not os.path.isdir(f"{glob.ROOT_UNZIP}/{bid}"):
        unzipfile()
    
    # check if exist re-builded beatmapsets and if not exist re-build beatmapset
    if noBg and noHitsound and noStoryboard:
        rebuildBeatmapset('all')
    elif noBg and noHitsound:
        rebuildBeatmapset('nobg&nohitsound')
    elif noBg and noStoryboard:
        rebuildBeatmapset('nobg&nostoryboard')
    elif noHitsound and noStoryboard:
        rebuildBeatmapset('nohitsound&nostoryboard')
    elif noBg:
        rebuildBeatmapset('nobg')
    elif noHitsound:
        rebuildBeatmapset('noHitsound')
    elif noStoryboard:
        rebuildBeatmapset('nostoryboard')
    
    return FileResponse(get_file_root(), media_type="application/x-osu-beatmap-archive", filename=generate_file_name())