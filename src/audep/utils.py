import chardet
import builtins
import re
import os
import platform


def open(file, mode='r', buffering=None, encoding=None, errors=None, newline=None, closefd=True):
    with builtins.open(file, 'rb') as f:
        result = chardet.detect(f.read())
    return builtins.open(file, mode, encoding=result['encoding'])


def get_encoding(file):
    with builtins.open(file, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


def check_null_raise(value, e):
    if not value:
        raise ParserError('Check null value is invalid: {}'.format(e))
    else:
        return value


def check_none_raise(value, e):
    if value == None:
        raise ParserError('Check none value is invalid: {}'.format(e))
    else:
        return value


def get_abspath(path_list):
    abs_paths = []
    if path_list:
        for path in path_list:
            abs_paths.append(os.path.abspath(path))
    return abs_paths


def get_files_by_dir(src, dst):
    src_tmp = os.path.abspath(src).replace("\\", "/")
    dst_tmp = dst.replace("\\", "/")
    src_filelist = []
    dst_filelist = []
    dst_dirlist = [dst]
    g = os.walk(src_tmp)
    for root, dirs, files in g:
        path = os.path.abspath(root).replace("\\", "/")
        for dir in dirs:
            tmp = root + '/' + dir
            dst_dirlist.append(tmp.replace(src_tmp, dst_tmp).replace("//", "/"))

        for filename in files:
            p = os.path.join(path, filename).replace("\\", "/")
            src_filelist.append(p)
            dst_filelist.append(p.replace(src_tmp, dst_tmp).replace("//", "/"))
    if src_filelist:
        return dst_dirlist, src_filelist, dst_filelist
    else:
        return None, None, None


def get_file_by_file(src, dst, is_dir):
    src_tmp = os.path.abspath(src).replace("\\", "/")
    dst_tmp = dst.replace("\\", "/")
    src_name = os.path.basename(src)
    if os.path.exists(src):
        if is_dir:
            dst_dir = dst_tmp
            src_file = src_tmp
            dst_file = (dst_dir + "/" + src_name).replace("//", "/")
        else:
            dst_dir = os.path.dirname(dst_tmp)
            src_file = src_tmp
            dst_file = dst_tmp

        return dst_dir, src_file, dst_file
    else:
        return None, None, None


_walk_files = '''
read_dir (){
for file in `ls $1`	
do
if [ -d $1"/"$file ] 
then
read_dir $1"/"$file
else
echo $1"/"$file
fi
done
}   
read_dir '''

_walk_dirs = '''
read_dir (){
for file in `ls $1`	
do
if [ -d $1"/"$file ] 
then
echo $1"/"$file
read_dir $1"/"$file
fi
done
}   
read_dir '''


def get_files_by_dir_from_remote(vme, src, dst):
    src_tmp = src.replace("\\", "/")
    dst_tmp = os.path.abspath(dst).replace("\\", "/")
    result_dir = vme.value.run(_walk_dirs + src_tmp, hide=True)
    result_file = vme.value.run(_walk_files + src_tmp, hide=True)
    src_filelist = []
    dst_filelist = []
    dst_dirlist = [dst.replace("//", "/").replace('/', '\\')]
    if result_dir:
        src_dirlist = re.split(r'[\s]', result_dir.stdout.replace("//", "/"))

    if result_file:
        src_filelist_temp = re.split(r'[\s]', result_file.stdout.replace("//", "/"))

    for d in src_dirlist:
        if d != '':
            if platform.system() == 'Windows':
                dst_dirlist.append(d.replace(src_tmp, dst_tmp).replace("//", "/").replace('/', '\\'))
            else:
                dst_dirlist.append(d.replace(src_tmp, dst_tmp).replace("//", "/"))

    for f in src_filelist_temp:
        if f != '':
            src_filelist.append(f)
            if platform.system() == 'Windows':
                dst_filelist.append(f.replace(src_tmp, dst_tmp).replace("//", "/").replace('/', '\\'))
            else:
                dst_filelist.append(f.replace(src_tmp, dst_tmp).replace("//", "/"))

    if src_filelist:
        return dst_dirlist, src_filelist, dst_filelist
    else:
        return None, None, None


def get_file_by_file_from_remote(vme, src, dst, is_dir):
    src_tmp = src.replace("\\", "/")
    dst_tmp = os.path.abspath(dst).replace("\\", "/")
    result = vme.value.run(f'test -f {src_tmp} && echo `readlink -f {src_tmp}`', hide=True)
    if result.return_code == 0:
        src_file_tmp = re.split(r'[\s]', result.stdout.replace("//", "/"))
        if len(src_file_tmp) > 0:
            src_name = os.path.basename(src_file_tmp[0])
            if is_dir:
                src_file = src_file_tmp[0]
                if platform.system() == 'Windows':
                    dst_dir = dst_tmp.replace('/', '\\')
                    dst_file = (dst_dir + "/" + src_name).replace("//", "/").replace('/', '\\')
                else:
                    dst_dir = dst_tmp
                    dst_file = (dst_dir + "/" + src_name).replace("//", "/")
            else:
                src_file = src_file_tmp[0]
                if platform.system() == 'Windows':
                    dst_dir = os.path.dirname(dst_tmp).replace('/', '\\')
                    dst_file = dst_tmp.replace('/', '\\')
                else:
                    dst_dir = os.path.dirname(dst_tmp)
                    dst_file = dst_tmp

            return dst_dir, src_file, dst_file
    else:
        return None, None, None


class ParserError(Exception):
    pass


class ActionError(Exception):
    pass


class CommandError(Exception):
    pass


class PluginError(Exception):
    pass


class ConfigError(Exception):
    pass


class FileError(Exception):
    pass


class ExecutorError(Exception):
    pass


class TemplateError(Exception):
    pass
