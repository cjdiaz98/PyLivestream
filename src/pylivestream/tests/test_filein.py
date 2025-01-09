import pytest
from pytest import approx
from pathlib import Path
import subprocess
import os
import sys
import importlib.resources

import pylivestream as pls

sites = ["youtube", "facebook"]
TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
ini = Path(__file__).parents[1] / "data/pylivestream.json"


def test_props():

    vid = importlib.resources.files("pylivestream.data").joinpath("bunny.avi")
    S = pls.FileIn(ini, websites=sites, infn=vid)
    for s in S.streams:
        assert "-re" in S.streams[s].cmd
        assert S.streams[s].fps == approx(24.0)

        if int(S.streams[s].res[1]) == 480:
            assert S.streams[s].video_kbps == 500
        elif int(S.streams[s].res[1]) == 720:
            assert S.streams[s].video_kbps == 1800


def test_audio():

    logo = importlib.resources.files("pylivestream.data").joinpath("logo.png")
    snd = importlib.resources.files("pylivestream.data").joinpath("orch_short.ogg")

    S = pls.FileIn(ini, websites=sites, infn=snd, image=logo)
    for s in S.streams:
        assert "-re" in S.streams[s].cmd
        assert S.streams[s].fps is None

        assert S.streams[s].video_kbps == 800


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI, reason="CI has no audio hardware typically")
def test_simple():
    """stream to localhost"""
    logo = importlib.resources.files("pylivestream.data").joinpath("logo.png")
    aud = importlib.resources.files("pylivestream.data").joinpath("orch_short.ogg")

    S = pls.FileIn(ini, websites="localhost", infn=aud, image=logo, yes=True, timeout=5)

    S.golive()


@pytest.mark.skipif(CI, reason="CI has no audio hardware typically")
def test_script():
    vid = importlib.resources.files("pylivestream.data").joinpath("bunny.avi")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pylivestream.fglob",
            str(vid),
            "localhost",
            str(ini),
            "--yes",
            "--timeout",
            "5",
        ],
        timeout=TIMEOUT,
    )
