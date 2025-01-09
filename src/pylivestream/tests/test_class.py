import pytest
from pytest import approx
from pathlib import Path
import importlib.resources

import pylivestream as pls


ini = Path(__file__).parents[1] / "data/pylivestream.json"


@pytest.mark.parametrize("rex", ("ffmpeg", "ffprobe"))
def test_exe(rex):
    exe = pls.ffmpeg.get_exe(rex)
    assert rex in exe


@pytest.mark.parametrize("inp", (None, ""))
def test_attrs(inp):
    assert not pls.utils.get_resolution(inp)

    vid = importlib.resources.files("pylivestream.data").joinpath("bunny.avi")
    assert pls.utils.get_resolution(vid) == [426, 240]
    assert pls.utils.get_framerate(vid) == approx(24.0)


def test_config_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        pls.Livestream(tmp_path / "nothere.json", "localhost")


def test_config_default(tmp_path):
    S = pls.Livestream(ini, "localhost")
    assert "localhost" in S.site
