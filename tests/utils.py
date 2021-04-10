from os import path, scandir

def make_files(tmpdir, game_name):
    """creates a typical game directory"""
    filenames = (
        game_name + ".gdi",
        game_name + "(track1).bin",
        game_name + "(track2).bin",
        game_name + "(track3).raw")
    game_dir = tmpdir.mkdir(game_name)
    file_extensions = list()
    for f in filenames:
        p = game_dir.join(f)
        p.write("")
        _1, ext = path.splitext(f)
        if ext not in file_extensions:
            file_extensions.append(ext)

    return game_dir, filenames, file_extensions

def check_filename(file, dirname):
    """makes sure the output file name is correct"""
    filename = path.basename(file)
    name, ext = path.splitext(filename)
    if ext.lower() == ".gdi":
        assert(name == "disc")
        return ".gdi"
    elif ext.lower() == ".raw" or ext.lower() == ".bin":
        assert(name[:5] == "track")
        try:
            int(name[5:])
            if ext.lower() == ".raw":
                return ".raw"
            else:
                return ".bin"
        except:                                 # pragma: no cover
            assert(False)
    elif ext.lower() == ".txt":
        assert(name == dirname)
        return ".txt"
    else:                                       # pragma: no cover
        print("name was: " + name)
        assert(False)

def check_files(directory, expected_exts):
    """ validates the filenames in a dir"""
    exts = dict.fromkeys(expected_exts, 0)
    dirname = path.basename(directory)
    with scandir(directory) as itr:
        for item in itr:
            if path.isfile(item):
                ext = check_filename(item.name, dirname)
                if ext in exts:
                    exts[ext] += 1
            elif path.isdir(item):
                continue
            else:                               # pragma: no cover
                assert(False)

    for count in exts.values():
        assert(count > 0)
