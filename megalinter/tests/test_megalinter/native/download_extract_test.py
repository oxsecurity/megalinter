import hashlib
import io
import os
import stat
import tarfile
import tempfile
import unittest
import zipfile

from megalinter.native import extract
from megalinter.native.context import NativeError
from megalinter.native.download import fetch_verified, sha256_of_file


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeOpener:
    def __init__(self, content):
        self.content = content
        self.calls = 0

    def open(self, request, timeout=None):
        self.calls += 1
        return FakeResponse(self.content)


def tar_bytes(entries, kind="w:gz"):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode=kind) as archive:
        for name, content, entry_type, link in entries:
            info = tarfile.TarInfo(name)
            info.type = entry_type
            if entry_type == tarfile.REGTYPE:
                info.size = len(content)
                info.mode = 0o755
                archive.addfile(info, io.BytesIO(content))
            else:
                info.linkname = link
                archive.addfile(info)
    return buffer.getvalue()


class DownloadTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.content = b"megalinter native"
        self.sha256 = hashlib.sha256(self.content).hexdigest()

    def test_download_verified_and_cached(self):
        opener = FakeOpener(self.content)
        path = fetch_verified(
            "https://example.com/a",
            self.sha256,
            len(self.content),
            self.folder,
            opener=opener,
        )
        self.assertEqual(sha256_of_file(path), self.sha256)
        fetch_verified(
            "https://example.com/a",
            self.sha256,
            len(self.content),
            self.folder,
            opener=opener,
        )
        self.assertEqual(opener.calls, 1)

    def test_sha256_mismatch_is_rejected_and_nothing_is_kept(self):
        with self.assertRaises(NativeError):
            fetch_verified(
                "https://example.com/a",
                "0" * 64,
                len(self.content),
                self.folder,
                opener=FakeOpener(self.content),
            )
        self.assertEqual(os.listdir(self.folder), [])

    def test_http_is_rejected(self):
        with self.assertRaises(NativeError):
            fetch_verified(
                "http://example.com/a",
                self.sha256,
                None,
                self.folder,
                opener=FakeOpener(self.content),
            )

    def test_larger_than_locked_size_is_rejected(self):
        with self.assertRaises(NativeError):
            fetch_verified(
                "https://example.com/a",
                self.sha256,
                3,
                self.folder,
                opener=FakeOpener(self.content),
            )

    def test_offline_requires_cache(self):
        with self.assertRaises(NativeError):
            fetch_verified(
                "https://example.com/a", self.sha256, None, self.folder, offline=True
            )


class ExtractTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.archive = os.path.join(tempfile.mkdtemp(), "archive")
        self.destination = os.path.join(self.folder, "dest")

    def write_tar(self, entries):
        with open(self.archive, "wb") as f:
            f.write(tar_bytes(entries))

    def test_tar_with_strip_components(self):
        self.write_tar([("tool-1.0/bin/tool", b"x", tarfile.REGTYPE, None)])
        extract.extract_archive(self.archive, "tar.gz", self.destination, 1)
        self.assertTrue(os.path.isfile(os.path.join(self.destination, "bin", "tool")))

    def test_tar_path_traversal_is_rejected(self):
        self.write_tar([("../evil", b"x", tarfile.REGTYPE, None)])
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "tar.gz", self.destination)
        self.assertFalse(os.path.exists(os.path.join(self.folder, "evil")))

    def test_tar_absolute_path_is_rejected(self):
        self.write_tar([("/tmp/evil", b"x", tarfile.REGTYPE, None)])
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "tar.gz", self.destination)

    def test_tar_symlink_escaping_is_rejected(self):
        self.write_tar([("link", b"", tarfile.SYMTYPE, "../../etc/passwd")])
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "tar.gz", self.destination)

    def test_tar_device_file_is_rejected(self):
        self.write_tar([("dev", b"", tarfile.CHRTYPE, "")])
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "tar.gz", self.destination)

    def test_tar_setuid_bit_is_dropped(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            info = tarfile.TarInfo("tool")
            info.size = 1
            info.mode = 0o4755
            archive.addfile(info, io.BytesIO(b"x"))
        with open(self.archive, "wb") as f:
            f.write(buffer.getvalue())
        extract.extract_archive(self.archive, "tar.gz", self.destination)
        if os.name == "posix":
            mode = os.stat(os.path.join(self.destination, "tool")).st_mode
            self.assertFalse(mode & stat.S_ISUID)

    def test_zip_path_traversal_is_rejected(self):
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("../evil", "x")
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "zip", self.destination)

    def test_zip_symlink_is_rejected(self):
        with zipfile.ZipFile(self.archive, "w") as archive:
            info = zipfile.ZipInfo("link")
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, "target")
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "zip", self.destination)

    def test_zip_extracts_files(self):
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("top/a.txt", "a")
        extract.extract_archive(self.archive, "zip", self.destination, 1)
        self.assertTrue(os.path.isfile(os.path.join(self.destination, "a.txt")))

    def test_single_file_keeps_given_name(self):
        with open(self.archive, "wb") as f:
            f.write(b"binary")
        extract.extract_archive(self.archive, "none", self.destination, name="tool")
        self.assertTrue(os.path.isfile(os.path.join(self.destination, "tool")))

    def test_single_file_name_cannot_escape(self):
        with open(self.archive, "wb") as f:
            f.write(b"binary")
        with self.assertRaises(NativeError):
            extract.extract_archive(self.archive, "none", self.destination, name="../x")
