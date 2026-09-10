import json, os, socket, sys

command = json.loads(sys.argv[2])
with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as channel:
    channel.settimeout(5)
    channel.connect("/native-control.sock")
    channel.sendall(sys.argv[1].encode("ascii"))
    if channel.recv(1) != b"1":
        sys.exit(7)
os.execvpe(command[0], command, os.environ)
