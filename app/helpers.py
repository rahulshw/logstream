def seek1(fileobj, nline, buffersize=1024):
    """ takes fileobject and an integer, nline to return a pointer to the file where nlineth line exist from last
    """
    fileobj.seek(0, 2)
    total_bytes = bytes = fileobj.tell()
    size = nline + 1  # will include the first line wholly
    block = -1
    while size >= 0 and bytes > 0:
        if bytes - buffersize > 0:
            fileobj.seek(total_bytes + block*buffersize, 0)
            data = fileobj.read(buffersize)
        else:
            fileobj.seek(0, 0)
            data = fileobj.read(bytes)
        linesfound = data.count('\n')
        size -= linesfound
        bytes -= buffersize
        block -= 1

    if fileobj.tell() != 0:
        print('last seek')
        while fileobj.read(1) != '\n':
            pass

    return fileobj


def seek2(fileobj, nline):
    """takes fileobject and an integer, nline to return a pointer to the file where nlineth line exist from last
    """
    line_pos =[]
    offset = 0
    for line in fileobj:
        line_pos.append(offset)
        offset += len(line)
    if len(line_pos) > nline:
        fileobj.seek(line_pos[-nline+1], 0)
    else:
        fileobj.seek(0, 0)
    return fileobj
