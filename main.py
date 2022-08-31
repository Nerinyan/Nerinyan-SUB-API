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
async def download_beatmapset(bid, noBg: bool = 0, noHitsound: bool = 0):
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
        # check exist already re-builed beatmapset
        if not os.path.isfile(f"{glob.ROOT_REBUILD}/{bid}/{filename}.osz"):
            with zipfile.ZipFile(f"{glob.ROOT_REBUILD}/{bid}/{filename}.osz", "w") as rebuild_ref:
                # backup now cwd
                owd = os.getcwd()
                # change cwd to unzipped root
                os.chdir(f"{glob.ROOT_UNZIP}/{bid}/")
                for f in os.listdir('./'):
                    if noBg and noHitsound:
                        # filtering image, hitsound files
                        if not f.endswith('.png') and not f.endswith('.jpg') and not any(x in f for x in hitsounds):
                            # add file to zip
                            rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    elif noBg:
                        # filtering image files
                        if not f.endswith('.png') and not f.endswith('.jpg'):
                            # add file to zip
                            rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                    elif noHitsound:
                        # filtering hitsound files
                        if not any(x in f for x in hitsounds):
                            # add file to zip
                            rebuild_ref.write(os.path.join(f"./", f), compress_type=zipfile.ZIP_DEFLATED)
                # return to default cwd
                os.chdir(owd)

    # get rebuiled file root
    def get_file_root():
        if noBg and noHitsound:
            return f"{glob.ROOT_REBUILD}/{bid}/all.osz"
        elif noBg:
            return f"{glob.ROOT_REBUILD}/{bid}/nobg.osz"
        elif noHitsound:
            return f"{glob.ROOT_REBUILD}/{bid}/noHitsound.osz"

    def generate_file_name():
        r = requests.get(f"{NERINYAN_API}/search?q={bid}")
        if r.status_code == 200:
            rbody = r.json()[0]
            r.close()
            return f"{bid} {rbody['artist_unicode']} - {rbody['title_unicode']}.osz"


    # beatmap file exist check
    checkfile()
    
    # If requested beatmapset is not unziped then unzip beatmapset
    if not os.path.isdir(f"{glob.ROOT_UNZIP}/{bid}"):
        unzipfile()
    
    # check exist re-builded beatmapsets and if not exist re-build beatmapset
    if noBg and noHitsound:
        rebuildBeatmapset('all')
    elif noBg:
        rebuildBeatmapset('nobg')
    elif noHitsound:
        rebuildBeatmapset('noHitsound')
    
    return FileResponse(get_file_root(), media_type="application/x-osu-beatmap-archive", filename=generate_file_name())