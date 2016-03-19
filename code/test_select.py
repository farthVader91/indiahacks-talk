import os
import select
import subprocess

proc1 = subprocess.Popen(['tail', '-f', 'sample.txt'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
proc2 = subprocess.Popen(['tail', '-f', 'test.txt'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

inputs = [proc1.stdout, proc2.stdout, proc1.stderr, proc2.stderr]
print inputs
outputs = []
exceptions = []

fd_buffer_map = {}

while inputs:
    readable, writeable, exceptional = select.select(inputs, outputs, exceptions)
    print readable
    for fd in readable:
        print fd.fileno()
        data = fd.read(8)
        data = data.rsplit(os.linesep, 1)
        if len(data) > 1:
            leftover = data[1]
        else:
            leftover = ''
        data = data[0]
        buffer_data = fd_buffer_map.get(fd.fileno(), '')
        if buffer_data:
            data = ''.join([buffer_data, data])
        if leftover:
            fd_buffer_map[fd.fileno()] = leftover
            continue
        print fd.fileno(), data
