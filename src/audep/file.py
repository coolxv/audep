import os
import re
import logging
import platform
from .utils import FileError
from .utils import get_files_by_dir, get_file_by_file, get_files_by_dir_from_remote, get_file_by_file_from_remote


class File:
    def __init__(self, vme):
        self._vme = vme

    def put_file(self, of):
        if of.lflag == 'd':
            remote_dirs, locs, remotes = get_files_by_dir(of.local, of.remote)
            if locs:
                for d in remote_dirs:
                    self._vme.run(f"mkdir -p {d}")
                for idx, val in enumerate(locs):
                    if self._vme.put(val, remotes[idx]) < self._vme.error:
                        raise FileError(f'put file failed when transfer file,{val} {remotes[idx]}')
                    if of.permit:
                        if of.re:
                            if re.search(of.re, os.path.basename(remotes[idx]), flags=0):
                                self._vme.run(f"chmod -f {of.permit} {remotes[idx]}")
                        else:
                            self._vme.run(f"chmod -f {of.permit} {remotes[idx]}")
            else:
                raise FileError('local dir is not exist when transfer files')
        else:
            remote_dir, local, remote = get_file_by_file(of.local, of.remote,
                                                         True if of.rflag == 'd' else False)
            if local:
                self._vme.run(f"mkdir -p {remote_dir}")
                if self._vme.put(local, remote) < self._vme.error:
                    raise FileError(f'put files failed when transfer files,{local} {remote}')
                if of.permit:
                    if of.re:
                        if re.search(of.re, os.path.basename(remote), flags=0):
                            self._vme.run(f"chmod -f {of.permit} {remote}")
                    else:
                        self._vme.run(f"chmod -f {of.permit} {remote}")
            else:
                raise FileError('local file is not exist when transfer file')

    def get_file(self, of):
        if of.rflag == 'd':
            local_dirs, remotes, locs = get_files_by_dir_from_remote(self._vme, of.remote, of.local)
            if remotes:
                for d in local_dirs:
                    if platform.system() == 'Windows':
                        self._vme.local(f"md {d}")
                    else:
                        self._vme.local(f"mkdir -p {d}")
                for idx, val in enumerate(remotes):
                    if self._vme.get(val, locs[idx]) < self._vme.error:
                        raise FileError(f'get file failed when transfer file,{val} {locs[idx]}')
                    if of.permit and platform.system() != 'Windows':
                        if of.re:
                            if re.search(of.re, os.path.basename(locs[idx]), flags=0):
                                self._vme.local(f"chmod -f {of.permit} {locs[idx]}")
                        else:
                            self._vme.local(f"chmod -f {of.permit} {locs[idx]}")
            else:
                raise FileError('remote dir is not exist when transfer files')
        else:
            local_dir, remote, loc = get_file_by_file_from_remote(self._vme, of.remote, of.local,
                                                         True if of.lflag == 'd' else False)
            if remote:
                if platform.system() == 'Windows':
                    self._vme.local(f"md {local_dir}")
                else:
                    self._vme.local(f"mkdir -p {local_dir}")

                if self._vme.get(remote, loc) < self._vme.error:
                    raise FileError(f'get file failed when transfer file,{remote} {loc}')
                if of.permit and platform.system() != 'Windows':
                    if of.re:
                        if re.search(of.re, os.path.basename(loc), flags=0):
                            self._vme.run(f"chmod -f {of.permit} {loc}")
                    else:
                        self._vme.run(f"chmod -f {of.permit} {loc}")
            else:
                raise FileError('remote file is not exist when transfer file')


if __name__ == '__main__':
    pass
