def seek1(fileobj, nline, buffersize=1024):
    """ takes fileobject and an integer, nline to return a pointer to the file where nlineth line exist from last
    """
    fileobj.seek(0, 2) # seeking to end
    total_bytes = bytes = fileobj.tell()
    size = nline + 1  # will include the first line wholly
    block = -1
    # iterate through the file starting from last one block at a time, and check if number of lines needed is reached
    while size >= 0 and bytes > 0:
        # check if bytes left to read is more than buffersize
        if bytes - buffersize > 0:
            fileobj.seek(total_bytes + block*buffersize, 0)
            data = fileobj.read(buffersize)
        else:
            fileobj.seek(0, 0)
            data = fileobj.read(bytes)
        # take account of how many lines reached
        linesfound = data.count('\n')
        size -= linesfound
        bytes -= buffersize
        block -= 1
    # seek to start of a line if file not seeked to start
    if fileobj.tell() != 0:
        while fileobj.read(1) != '\n':
            pass

    return fileobj


def seek2(fileobj, nline):
    """takes fileobject and an integer, nline to return a pointer to the file where nlineth line exist from last
    """
    line_pos =[]
    offset = 0
    # getting pointers to each line into line_pos array
    for line in fileobj:
        line_pos.append(offset)
        offset += len(line)
    # if numer of lines demanded is more than number of lines present in the file
    if len(line_pos) > nline:
        fileobj.seek(line_pos[-nline], 0)
    else:
        fileobj.seek(0, 0)
    return fileobj
