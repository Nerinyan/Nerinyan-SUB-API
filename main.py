import os
import re
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
    
    async def checkfile():
        if not os.path.isfile(f"{glob.ROOT_BEATMAP}/{bid}.osz"):
            with requests.get(f"{NERINYAN_API}/d/{bid}", stream=True) as req:
                req.raise_for_status()
                with open (f"{glob.ROOT_UNZIP}/{bid}.osz", 'wb') as f:
                    for chunk in req.iter_content(chunk_size=8192):
                        f.write(chunk)
            await unzipfile(istemp=True)


    async def unzipfile(istemp: bool = 0):
        if not istemp:
            with zipfile.ZipFile(f"{glob.ROOT_BEATMAP}/{bid}.osz", 'r') as beatmap_ref:
                beatmap_ref.extractall(f"{glob.ROOT_UNZIP}/{bid}")
        else:
            with zipfile.ZipFile(f"{glob.ROOT_UNZIP}/{bid}.osz", 'r') as beatmap_ref:
                beatmap_ref.extractall(f"{glob.ROOT_UNZIP}/{bid}")

    async def rebuildBeatmapset(filename):
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
    async def get_file_root():
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

    async def generate_file_name():
        r = requests.get(f"{NERINYAN_API}/search?q={bid}")
        if r.status_code == 200:
            rbody = r.json()[0]
            r.close()
            FILETYPE = ''
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
    await checkfile()
    
    # If requested beatmapset is not unziped then unzip beatmapset
    if not os.path.isdir(f"{glob.ROOT_UNZIP}/{bid}"):
        await unzipfile()
    
    # check if exist re-builded beatmapsets and if not exist re-build beatmapset
    if noBg and noHitsound and noStoryboard:
        await rebuildBeatmapset('all')
    elif noBg and noHitsound:
        await rebuildBeatmapset('nobg&nohitsound')
    elif noBg and noStoryboard:
        await rebuildBeatmapset('nobg&nostoryboard')
    elif noHitsound and noStoryboard:
        await rebuildBeatmapset('nohitsound&nostoryboard')
    elif noBg:
        await rebuildBeatmapset('nobg')
    elif noHitsound:
        await rebuildBeatmapset('noHitsound')
    elif noStoryboard:
        await rebuildBeatmapset('nostoryboard')
    
    return FileResponse(await get_file_root(), media_type="application/x-osu-beatmap-archive", filename=await generate_file_name())


@app.get("/bg/{bid}")
async def beatmap_bg(bid):
    async def check_request_is_set_or_beatmap():
        with requests.get(f"{NERINYAN_API}/search?q={bid}", stream=True) as req:
            req.raise_for_status()
            if req.status_code == 200:
                body = req.json()[0]
                if int(bid) == body['id']:
                    return ['sid', body['id']]
                for bmap in body['beatmaps']:
                    if int(bmap['id']) == int(bid):
                        return ['bid', body['id'], bmap['version']]

    async def checkfile(bbid: int = 0):
        if not os.path.isfile(f"{glob.ROOT_BEATMAP}/{bbid}.osz"):
            with requests.get(f"{NERINYAN_API}/d/{bbid}", stream=True) as req:
                req.raise_for_status()
                with open (f"{glob.ROOT_UNZIP}/{bbid}.osz", 'wb') as f:
                    for chunk in req.iter_content(chunk_size=8192):
                        f.write(chunk)
            await unzipfile(bbid=bbid, istemp=True)

    async def unzipfile(bbid: int = 0, istemp: bool = 0):
        if not istemp:
            with zipfile.ZipFile(f"{glob.ROOT_BEATMAP}/{bbid}.osz", 'r') as beatmap_ref:
                beatmap_ref.extractall(f"{glob.ROOT_UNZIP}/{bbid}")
        else:
            with zipfile.ZipFile(f"{glob.ROOT_UNZIP}/{bbid}.osz", 'r') as beatmap_ref:
                beatmap_ref.extractall(f"{glob.ROOT_UNZIP}/{bbid}")

    async def get_file_root(isBeatmap: bool = 0, bbid: int = 0, req: list = []):
        # backup now cwd
        owd = os.getcwd()
        # change cwd to unzipped root
        os.chdir(f"{glob.ROOT_UNZIP}/{bbid}/")
        for f in os.listdir('./'):
            if not isBeatmap:
                if f.endswith('.png') or f.endswith('.jpg'):
                    # return to default cwd
                    os.chdir(owd)
                    return f"{glob.ROOT_UNZIP}/{bbid}/{f}"
            else:
                if req[2] in f:
                    with open(f, 'r', encoding='UTF-8') as ff:
                        img_line = re.compile(r'(?<=0,0,").+(?=",0,0)').search(str(ff.readlines())).group()
                    # return to default cwd
                    os.chdir(owd)
                    return f"{glob.ROOT_UNZIP}/{bbid}/{img_line}"

    # check request is beatmapset or beatmap
    req = await check_request_is_set_or_beatmap()

    # beatmap file exist check
    await checkfile(bbid=req[1])

    # If requested beatmapset is not unziped then unzip beatmapset
    if not os.path.isdir(f"{glob.ROOT_UNZIP}/{req[1]}"):
        await unzipfile(bbid=req[1])

    return FileResponse(await get_file_root(isBeatmap=False if req[0] == 'sid' else True, bbid=req[1], req=req))