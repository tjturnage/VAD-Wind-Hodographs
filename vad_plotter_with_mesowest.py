# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 12:52:55 2019

@author: tjtur
"""
import math
import os
import sys
import shutil
import requests
from datetime import datetime


try:
    os.listdir('/usr')
    windows = False
    base_dir = '/var/www/html'
    scripts_dir = '/data/scripts'
    base_gis_dir = '/data/GIS'
    sys.path.append(os.path.join(scripts_dir,'resources'))
    vwp_script_path = os.path.join(scripts_dir,'vad-plotter-master','vad.py')
    display_dir = os.path.join(base_dir,'images','VWP')
    archive_dir = os.path.join(display_dir,'archive')
    py_call = '/usr1/anaconda3/bin/python '
except:
    windows = True
    base_dir = 'C:/data'
    scripts_dir = 'C:/data/scripts'
    base_gis_dir = 'C:/data/GIS'
    display_dir = os.path.join(base_dir,'images','VWP')
    archive_dir = os.path.join(display_dir,'archive')
    sys.path.append(os.path.join(scripts_dir,'resources'))
    vwp_script_path = os.path.join(scripts_dir,'vad-plotter-master','vad.py')
    py_call = 'python '

os.makedirs(archive_dir, exist_ok = True)
os.makedirs(display_dir, exist_ok = True)

"""
radar_metar_dict = {'KGRR':{'metar':'kgrr','json':None},
                    'KAPX':{'metar':'kglr','json':None},
                    'KDTX':{'metar':'kptk','json':None},
                    'KMKX':{'metar':'kues','json':None}}
"""

class Mesowest:
    def __init__(self, radar, stid, elements, units, archive=False):

        API_ROOT = "https://api.synopticdata.com/v2/"
        API_TOKEN = "292d36a692d74badb6ca011f4413ae1b"
        nowTime = datetime.utcnow()
        time_str = datetime.strftime(nowTime,'%Y%m%d%H%M')
        self.obtime_str = time_str
        self.stid = stid
        self.radar = radar
        self.elements = elements


        if archive:
            api_arguments = {"token":API_TOKEN,"state":"mi","network":"1,2,71,96,162,3001", "vars": varStr, "units": units, 'attime': time_str, 'within':'30' }
            #api_arguments = {"token":API_TOKEN,"cwa":"bmx", "vars": varStr, "units": unitsStr, 'attime': timeStr, 'within':'40' }
            api_request_url = os.path.join(API_ROOT, "stations/nearesttime")
        else:
            api_arguments = {"token":API_TOKEN,"stid":stid, "vars": elements, "units": units}
            api_request_url = os.path.join(API_ROOT, "stations/latest")
    
        req = requests.get(api_request_url, params=api_arguments)
        jas = req.json()


        self.wdir = jas['STATION'][0]['OBSERVATIONS']['wind_direction_value_1']['value']
        self.wspd = jas['STATION'][0]['OBSERVATIONS']['wind_speed_value_1']['value']
        self.lat = jas['STATION'][0]['LATITUDE']
        self.lon = jas['STATION'][0]['LONGITUDE']
        self.wind_str = f'{self.wdir:.0f}/{self.wspd:.0f}'
        self.archive_fname = radar + '_' + time_str + '.png'
        self.archive_fpath = os.path.join(archive_dir,self.archive_fname)
        self.current_fname = radar + '.png'
        self.current_fpath = os.path.join(display_dir,self.current_fname)

        self.cmd_str = py_call + vwp_script_path + ' ' + radar + ' -s ' + self.wind_str + ' -f ' + self.archive_fpath + ' -x'
        
        


elements = 'wind_speed,wind_direction,wind_gust'
units = 'speed|kts,precip|in'


nowTime = datetime.utcnow()
time_str = datetime.strftime(nowTime,'%Y%m%d%H%M')


grr = Mesowest('KGRR','kgrr',elements,units)
print(grr.cmd_str)
os.system(grr.cmd_str)
shutil.copy2(grr.archive_fpath,grr.current_fpath)

dtx = Mesowest('KDTX','kptk',elements,units)
os.system(dtx.cmd_str)
shutil.copy2(dtx.archive_fpath,dtx.current_fpath)

mkx = Mesowest('KMKX','kues',elements,units)
os.system(mkx.cmd_str)
shutil.copy2(mkx.archive_fpath,mkx.current_fpath)


