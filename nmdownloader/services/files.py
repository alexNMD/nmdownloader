import logging
import tarfile
import zipfile

import rarfile

logger = logging.getLogger("celery")


class ListCompressArchiveService:
    def __init__(self):
        self.supported_format = {
            ".zip": self._list_zip_contents,
            ".tar": self._list_tar_contents,
            ".tar.gz": self._list_tar_contents,
            ".tgz": self._list_tar_contents,
            ".tar.bz2": self._list_tar_contents,
            ".tbz": self._list_tar_contents,
            ".tar.xz": self._list_tar_contents,
            ".txz": self._list_tar_contents,
            ".rar": self._list_rar_contents,
        }

    def list_archive(self, extension: str, path: str) -> list:
        if not (list_method := self.supported_format.get(extension)):
            raise NotImplementedError(f"{extension} is not supported")

        return list_method(path=path)

    @classmethod
    def _list_zip_contents(cls, path: str) -> list:
        with zipfile.ZipFile(path, "r") as archive:
            return archive.namelist()

    @classmethod
    def _list_tar_contents(cls, path: str) -> list:
        with tarfile.open(path, "r:*") as archive:
            return archive.getnames()

    @classmethod
    def _list_rar_contents(cls, path: str) -> list:
        with rarfile.RarFile(path) as archive:
            return archive.namelist()
