from os import path, scandir

def make_files(tmpdir, game_name):
    """creates a typical game directory"""
    filenames = (
        game_name + ".gdi",
        game_name + "(track1).bin",
        game_name + "(track2).bin",
        game_name + "(track3).raw")
    game_dir = tmpdir.mkdir(game_name)
    for f in filenames:
        p = game_dir.join(f)
        p.write("")

    return game_dir, filenames

def check_filename(file, dirname):
    """makes sure the output file name is correct"""
    filename = path.basename(file)
    name, ext = path.splitext(filename)
    if ext.lower() == ".gdi":
        assert(name == "disc")
    elif ext.lower() == ".raw" or ext.lower() == ".bin":
        assert(name[:5] == "track")
        try:
            int(name[5:])
        except:                                 # pragma: no cover
            assert(False)
    elif ext.lower() == ".txt":
        assert(name == dirname)
    else:                                       # pragma: no cover
        print("name was: " + name)
        assert(False)

def check_files(directory):
    """ validates the filenames in a dir"""
    dirname = path.basename(directory)
    with scandir(directory) as itr:
        for item in itr:
            if path.isfile(item):
                check_filename(item, dirname)
            elif path.isdir(item):
                continue
            else:                               # pragma: no cover
                assert(False)
