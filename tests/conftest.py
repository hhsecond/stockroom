from pathlib import Path
import shutil
import pytest
import hangar
import numpy as np
from stockroom import StockRoom, init_repo


@pytest.fixture()
def managed_tmpdir(monkeypatch, tmp_path):
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, 'map_size', 2_000_000)
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, 'map_size', 2_000_000)
    monkeypatch.setattr(hangar.backends.hdf5_00, 'COLLECTION_COUNT', 10)
    monkeypatch.setattr(hangar.backends.hdf5_00, 'COLLECTION_SIZE', 50)
    monkeypatch.setattr(hangar.backends.hdf5_01, 'COLLECTION_COUNT', 10)
    monkeypatch.setattr(hangar.backends.hdf5_01, 'COLLECTION_SIZE', 50)
    monkeypatch.setattr(hangar.backends.numpy_10, 'COLLECTION_SIZE', 50)
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.fixture()
def repo(monkeypatch, managed_tmpdir):
    cwd = Path(managed_tmpdir)
    monkeypatch.setattr(Path, 'cwd', lambda: cwd)
    cwd.joinpath(".git").mkdir()
    cwd.joinpath(".gitignore").touch()
    init_repo('s', 'a@b.c', overwrite=True)
    yield None


@pytest.fixture()
def repo_with_aset(repo):
    repo = hangar.Repository(Path.cwd())
    co = repo.checkout(write=True)
    arr = np.arange(20).reshape(4, 5)
    co.arraysets.init_arrayset('aset', prototype=arr)
    co.commit('init aset')
    co.close()
    yield None
    repo._env._close_environments()


@pytest.fixture()
def stock(repo_with_aset):
    stock_obj = StockRoom()
    yield stock_obj
    stock_obj._repo.hangar_repository._env._close_environments()
