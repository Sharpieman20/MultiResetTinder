
import requests
import subprocess as sp
import shlex


def run_cmd(cmd):
    sp.call(shlex.split(cmd))

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/MultiResetTinder/main/release.txt'

release_url = requests.get(get_release_url).text.rstrip()
 
r = requests.get(release_url, allow_redirects=True)
open('release.zip', 'wb').write(r.content)

directory_to_extract_to = 'directory'

import zipfile
with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
    zip_ref.extractall(directory_to_extract_to)

run_cmd('pip install -r src/requirements.txt')

