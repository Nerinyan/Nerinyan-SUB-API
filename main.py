import os
import re
import json
import zipfile
import requests
import pathlib
import datetime
import time

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from common import glob
from modules import config

glob.BASEROOT = pathlib.Path(__file__).parent
config.CONFIG_LOADER()
app = FastAPI()
NERINYAN_API = "https://api.nerinyan.moe"

@app.get("/")
async def root():
    return {"msg": "oh, hi!! (>///<)"}


@app.get("/notification")
async def notification():
    try:
        with open("./notification.json", "r") as r:
            return json.load(r)
    except Exception as e:
        return {'error': str(e)}
    

@app.get("/d/{bid}")
async def download_beatmapset(bid, noVideo: bool = 0, noBg: bool = 0, noHitsound: bool = 0, noStoryboard: bool = 0, nv: bool = 0, nb: bool = 0, nh: bool = 0, nsb: bool = 0):
    noVideo = noVideo | nv
    noBg = noBg | nb
    noHitsound = noHitsound | nh
    noStoryboard = noStoryboard | nsb

    if noVideo == False and noBg == False and noHitsound == False and noStoryboard == False:
        return JSONResponse({"error": "parameter not detected"})

    async def checkfile_is_latest():
        url = f"{NERINYAN_API}/search?q={bid}&s=all&nsfw=true&option=s"
        with requests.get(url, stream=True) as req:
            req.raise_for_status()
            if req.status_code == 200:
                body = req.json()[0]
                db_time = int(time.mktime(datetime.datetime.strptime(body['last_updated'], "%Y-%m-%d %H:%M:%S").timetuple()))
                file_time = int(os.path.getmtime(f"{glob.ROOT_BEATMAP}/{bid}.osz"))
                if db_time - file_time >= 0:
                    print(f'{bid} - file not latest. so cleanup files')
                    if os.path.isfile(f"{glob.ROOT_BEATMAP}/{bid}.osz"):
                        os.remove(f"{glob.ROOT_BEATMAP}/{bid}.osz")
                    if os.path.isfile(f"{glob.ROOT_UNZIP}/{bid}.osz"):
                        os.remove(f"{glob.ROOT_UNZIP}/{bid}.osz")
                    os.rmdir(f"{glob.ROOT_UNZIP}/{bid}/")
                    os.rmdir(f"{glob.ROOT_REBUILD}/{bid}/")


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
                    elif noStoryboard and not noBg and not noHitsound:
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
        root = f"{glob.ROOT_REBUILD}/{bid}/{'novideo/' if noVideo else ''}"
        if noBg and noHitsound and noStoryboard:
            return f"{root}all.osz"
        if noBg and noHitsound and not noStoryboard:
            return f"{root}nobg&nohitsound.osz"
        if noBg and noStoryboard and not noHitsound:
            return f"{root}nobg&nostoryboard.osz"
        if noHitsound and noStoryboard and not noBg:
            return f"{root}nohitsound&nostoryboard.osz"
        if noBg:
            return f"{root}nobg.osz"
        if noHitsound:
            return f"{root}noHitsound.osz"
        if noStoryboard:
            return f"{root}nostoryboard.osz"


    async def generate_file_name():
        r = requests.get(f"{NERINYAN_API}/search?q={bid}&s=all&nsfw=true&option=s")
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
            return f"{bid} {rbody['artist']} - {rbody['title']}.osz"

    await checkfile_is_latest()

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


@app.get("/bg/{beatmapid}")
async def beatmap_bg(beatmapid):
    if int(beatmapid) < 0:
        bid = -int(beatmapid)
    else:
        bid = int(beatmapid)

    async def check_request_is_set_or_beatmap(re: bool = 0):
        url = f"{NERINYAN_API}/search?q={bid}&s=all&nsfw=true"
        if int(beatmapid) < 0 and not re:
            url += "&option=s"
        if re:
            url += "&option=m"
        with requests.get(url, stream=True) as req:
            req.raise_for_status()
            if req.status_code == 200:
                if len(req.json()) > 1:
                    return await check_request_is_set_or_beatmap(re=True)
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
        try:
            # change cwd to unzipped root
            os.chdir(f"{glob.ROOT_UNZIP}/{bbid}/")
            for f in os.listdir('./'):
                if not isBeatmap:
                    if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg'):
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
        except Exception as e:
            return "ERROR"

    # check request is beatmapset or beatmap3
    req = await check_request_is_set_or_beatmap()
    if req[0] == 'error':
        return JSONResponse(content={"error": "I can't to specify if what you requested is beatmapset id or beatmap id. But if you requested beatmapset id, add '-' before beatmapset id.",}, status_code=404)

    try:
        FuckManiaKey = re.compile(r'(\[[0-9]K\] )').search(str(req[2])).group()
        if len(FuckManiaKey) > 0:
            req[2] = req[2].replace(FuckManiaKey, "")
    except:
        pass

    try:
        # beatmap file exist check
        await checkfile(bbid=req[1])

        # If requested beatmapset is not unziped then unzip beatmapset
        if not os.path.isdir(f"{glob.ROOT_UNZIP}/{req[1]}"):
            await unzipfile(bbid=req[1])
    except:
        return JSONResponse(content={"error": "An error occurred while trying to find BG."}, status_code=404)

    fileROOT = await get_file_root(isBeatmap=False if req[0] == 'sid' else True, bbid=req[1], req=req)

    if fileROOT is not "ERROR":
        return FileResponse(fileROOT)
    else:
        return JSONResponse(content={"error": "An error occurred while trying to find BG."}, status_code=404)