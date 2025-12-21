import sys
import os
import time
import hashlib, io, hmac
import shutil




SCRIPT_NAME = sys.argv[0]
SRC_PATH = sys.argv[1]
REPLICA_PATH = sys.argv[2]
INTERVAL = sys.argv[3]
SYNC_COUNT = sys.argv[4]
# LOG_PATH = sys.argv[5]



with os.scandir(SRC_PATH) as files:
    for item in files:
        print (f"{item.name} is a {'Directory'if item.is_dir() else 'file'} and it is located in {item.path}")
#
#
#
# # print("Total arguments:", len(sys.argv))
# # print("Script name:", sys.argv[0])
# #
# SRC_PATH = sys.argv[1]
# REPLICA_PATH = sys.argv[2]
#
#
# # print(SRC_PATH)
# #
# # files  = os.listdir(SRC_PATH)
# # for file in files:
# #     print(file)
# # print(SRC_PATH)
#
#
#
# files  = os.listdir(SRC_PATH)
# for file in files:
#     shutil.copy(SRC_PATH+file, REPLICA_PATH)
#
#
# # time_thing = os.path.getmtime(SRC_PATH + 'thing.txt')
# # time_helo = os.path.getmtime(SRC_PATH + 'helo.txt')
# #
# # if time_thing > time_helo:
# #     print('Hello is less')
# # else:
# #     print('Thing is less')
# # for file in files:
# #
# #     creation_time = os.path.getctime(SRC_PATH + file)
# #     access_time = os.path.getatime(SRC_PATH + file)
# #     modification_time = os.path.getmtime(SRC_PATH + file)
# #     print(f'Creation time of {file}:', time.ctime(creation_time))
# #     print(f'Access time of {file}:', time.ctime(access_time))
# #     print(f'Modification time of {file}:', time.ctime(modification_time))
# #
#
# # m = hashlib.md5()
# # m.update(b"hello{5}")
# # m.hexdigest()
# #
# # c = hashlib.md5(b"hello{5}")
# # c.hexdigest()
# # c.update(b'6')
# # m.update(b'6')
# # a = c.hexdigest()
# # c.update(b'hello')
# # b = c.hexdigest()
# # c.
# #
# # print(a)
# # print(b)
#
#
#
#
