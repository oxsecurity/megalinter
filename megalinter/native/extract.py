import gzip
import os
import posixpath
import shutil
import stat
import tarfile
import zipfile

from megalinter.native.context import NativeError

ARCHIVE_TYPES = ["none", "zip", "tar.gz", "tar.xz", "tar.bz2", "gz"]
TAR_MODES = {"tar.gz": "r:gz", "tar.xz": "r:xz", "tar.bz2": "r:bz2"}
ZIP_UNIX_MODE_SHIFT = 16


def strip_member_name(name, strip_components):
    parts = [
        part for part in name.replace("\\", "/").split("/") if part not in ("", ".")
    ]
    if ".." in parts or (
        parts and (parts[0].endswith(":") or name.startswith(("/", "\\")))
    ):
        raise NativeError(f"Unsafe path in archive: {name}")
    stripped = parts[strip_components:]
    return posixpath.join(*stripped) if stripped else None


def safe_destination(destination, relative_name):
    target = os.path.realpath(os.path.join(destination, relative_name))
    root = os.path.realpath(destination)
    if target != root and not target.startswith(root + os.sep):
        raise NativeError(
            f"Archive entry escapes the install directory: {relative_name}"
        )
    return target


def extract_tar(path, kind, destination, strip_components):
    with tarfile.open(path, TAR_MODES[kind]) as archive:
        for member in archive:
            relative = strip_member_name(member.name, strip_components)
            if relative is None:
                continue
            if member.issym() or member.islnk():
                link_target = member.linkname.replace("\\", "/")
                if link_target.startswith("/") or ".." in link_target.split("/"):
                    raise NativeError(
                        f"Unsafe link in archive: {member.name} -> {member.linkname}"
                    )
            if not (
                member.isfile() or member.isdir() or member.issym() or member.islnk()
            ):
                raise NativeError(f"Unsupported entry type in archive: {member.name}")
            member.name = relative
            safe_destination(destination, relative)
            archive.extract(member, destination, filter="data")


def extract_zip(path, destination, strip_components):
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            relative = strip_member_name(info.filename, strip_components)
            if relative is None:
                continue
            mode = info.external_attr >> ZIP_UNIX_MODE_SHIFT
            if stat.S_ISLNK(mode):
                raise NativeError(f"Symbolic link in zip archive: {info.filename}")
            target = safe_destination(destination, relative)
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with archive.open(info) as source, open(target, "wb") as out:
                shutil.copyfileobj(source, out)
            if mode & stat.S_IXUSR:
                os.chmod(target, 0o755)


def extract_archive(path, kind, destination, strip_components=0, name=None):
    os.makedirs(destination, exist_ok=True)
    if kind in TAR_MODES:
        extract_tar(path, kind, destination, strip_components)
    elif kind == "zip":
        extract_zip(path, destination, strip_components)
    elif kind == "gz":
        target = safe_destination(destination, name or os.path.basename(path))
        with gzip.open(path, "rb") as source, open(target, "wb") as out:
            shutil.copyfileobj(source, out)
        os.chmod(target, 0o755)
    elif kind == "none":
        target = safe_destination(destination, name or os.path.basename(path))
        shutil.copyfile(path, target)
        os.chmod(target, 0o755)
    else:
        raise NativeError(f"Unknown archive type: {kind}")
