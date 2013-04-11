# -*- coding: utf-8 -*-
from Crypto import Cipher
from zipfile import ZipFile
import Crypto.Cipher.AES
import Crypto.Random
import Crypto.Util.Counter
import binascii
import bs.utils
import bz2
import gzip
import hashlib
import itertools
import logging
import lzma
import math
import os
import random
import sqlite3
import tarfile
import tempfile
import time
import zipfile

###############################################################################
##    [NAME]                                                                 ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2012 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Nov 25, 2012                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

#import os
#
#
#class Event(object):
#    def __init__(self):
#        self.handlers = set()
#
#    def handle(self, handler):
#        self.handlers.add(handler)
#        return self
#
#    def unhandle(self, handler):
#        try:
#            self.handlers.remove(handler)
#        except:
#            raise ValueError("Handler is not handling this event, so can not "\
#                             "unhandle it.")
#        return self
#
#    def fire(self, *args, **kargs):
#        for handler in self.handlers:
#            handler(*args, **kargs)
#
#    def get_handler_count(self):
#        return len(self.handlers)
#
#    __iadd__ = handle
#    __isub__ = unhandle
#    __call__ = fire
#    __len__ = get_handler_count
#
#
#class FileWatcher(object):
#    def __init__(self):
#        self.file_changed = Event()
#
#    def watch_files(self):
#        source_path = os.path.realpath("Z:/compress_encrypt")
#        self.file_changed(source_path)
#
#
#def log_file_change(source_path):
#    print("%r changed." % (source_path,))
#
#
#def log_file_change_2(x):
#    print(x)
#
#watcher = FileWatcher()
#watcher.file_changed += log_file_change
#watcher.file_changed += log_file_change_2
#watcher.watch_files()

#file_in = os.path.realpath("Z:\\compress_encrypt.FVA")
#file_out = os.path.realpath("Z:\\out.txt")

#    import os
#    import re
#
#    #file_in = os.path.realpath("Z:/in.txt")
#    #file_out = os.path.realpath("Z:/out.txt")
#
#
#    file_in = os.path.realpath("path/to/log_file.txt")
#    file_out = os.path.realpath("path/to/output_file.txt")
#
#    def extract_lines():
#        with open(file_in, "r") as f_in:
#            for line in f_in.readlines():
#                res = re.search("(PUT_LOG\()(.*)(\)\;)", line)
#                for segment in res.group(2).split(", "):
#                    print(segment)
#
#    extract_lines()

###############################################################################
#
#import os
#import re
#
#
#def extract_lines(file_in, file_out, strings_to_filter):
#    with open(file_in) as f_in, open(file_out, "a+") as f_out:
#        for line in f_in:
#            res = re.search("(PUT_LOG\()(.*)(\)\;)", line)
#            if res is not None:
#                i = 0
#                for segment in res.group(2).split(","):
#                    segment = segment.strip()
#                    if segment in strings_to_filter and i < 2:
#                        print(segment, file=f_out)
#                        i += 1
#
#extract_lines(
#              os.path.realpath("Z:/in.txt"),
#              os.path.realpath("Z:/out.txt"),
#              [
#               "CAPTIVE_EXECUTE_CMD",
#               "CAPTIVE_EXECUTE_CMD_FAILED",
#               "CAPTIVE_RECVD_SIGCHLD",
#               "LOG_LEVEL_DEBUG",
#               "LOG_LEVEL_DEBUG_ERR"
#               ]
#              )
#
###############################################################################


#time_start = time.time()
#conn = sqlite3.connect("Z:\\compress_encrypt.sqlite")
#conn.execute("DROP TABLE compress_encrypt")
#conn.execute("CREATE TABLE compress_encrypt ('inode' INTEGER)")
#conn.commit()
#for folder_path, folders, files in os.walk("Z:\\files"):
#    for file in files:
#        inode = os.stat(os.path.join(folder_path, file)).st_ino
#        conn.execute("INSERT INTO compress_encrypt VALUES (?)", (inode, ))
#        print(os.path.join(folder_path, file))
#print(time.time() - time_start)
#conn.commit()
#print(time.time() - time_start)

#i = 0
#for inode in (x[0] for x in conn.execute("SELECT * FROM compress_encrypt").fetchall()):
#    if len(conn.execute("SELECT * FROM compress_encrypt WHERE inode = ?", (inode, )).fetchall()) > 1:
#        print("NOT GOOD: %s" % (inode, ))
#    print(i)
#    i += 1


#print("Finding duplicates...")
#time_start = time.time()
#print(any(x == y for x, y in itertools.combinations(INODES, 2)))
#print(time.time() - time_start)

#for INODE in INODES:
#    if INODE not in INODES_2:
#        INODES_2.append(INODE)
#    else:
#        print(INODE)
#    print(len(INODES_2))



#print("DONE")

###############################################################################

#def write_file_random_content(target_directory_path, file_size_min, file_size_max):
#    target_file_path = os.path.join(target_directory_path, "")
#    file_size_rand = random.randint(file_size_min, file_size_max)
#    if not os.path.isdir(target_directory_path):
#        os.makedirs(target_directory_path)
#
#    while os.path.isfile(target_file_path) or\
#        os.path.isdir(target_file_path):
#        name = str(random.randint(1000000000000, 9999999999999))
#        target_file_path = os.path.join(os.path.split(target_directory_path)[0], name)
#
#    contents = random.randint(1000000000000000, 9999999999999999)
#    contents = str(contents) * 64 * file_size_rand
#
#    contents = bytes(contents, "utf-8")
#
#    with open(target_file_path, "wb") as out:
#        out.write(contents)
#
#for i in range(10):
#    for j in range(10):
#        write_file_random_content("Y:\\_TMP\\bsTest\\s2\\%s\\" % i, 1 * pow(2, 10), 1 * pow(2, 10))

###############################################################################


#sources = ["Y:\\_TMP\\bsTest\\s1\\0\\"]
##sources = [r"W:\_movies\Star Trek - Deep Space 9\Star Trek DS9 Season 3"]
#target = "Y:\\_TMP\\bsTest\\t2"
#
#
#def benchmark_gzip(level=9):
#    time_start = time.time()
#    for source in sources:
#        for folder_path, folders, files in os.walk(source):
#            for file in files:
#                source_file_path = os.path.join(folder_path, file)
#                target_file_path = os.path.join(target, file + ".gz")
#                with open(source_file_path, "rb") as f_in:
#                    with gzip.open(target_file_path, "wb", compresslevel=level) as f_out:
#                        f_out.writelines(f_in)
#    print("GZip: Time elapsed: %.2fs" % (time.time() - time_start), )
#
#
#def benchmark_bz2(level=9):
#    time_start = time.time()
#    for source in sources:
#        for folder_path, folders, files in os.walk(source):
#            for file in files:
#                source_file_path = os.path.join(folder_path, file)
#                target_file_path = os.path.join(target, file + ".bz2")
#                with open(source_file_path, "rb") as f_in:
#                    with bz2.open(target_file_path, "wb", compresslevel=level) as f_out:
#                        f_out.writelines(f_in)
#    print("bz2: Time elapsed: %.2fs" % (time.time() - time_start), )
#
#
#def benchmark_lzma():
#    time_start = time.time()
#    for source in sources:
#        for folder_path, folders, files in os.walk(source):
#            for file in files:
#                source_file_path = os.path.join(folder_path, file)
#                target_file_path = os.path.join(target, file + ".xz")
#                with open(source_file_path, "rb") as f_in:
#                    with lzma.open(target_file_path, "wb") as f_out:
#                        f_out.writelines(f_in)
#    print("Lzma: Time elapsed: %.2fs" % (time.time() - time_start), )
#
#
#def benchmark_tar_gzip():
#    time_start = time.time()
#    target_file_path = os.path.join(target, "tmp.tar.gz")  # os.path.join(target, file + ".xz")
#    with tarfile.open(target_file_path, "w:gz") as f_out:
#        for source in sources:
#            for folder_path, folders, files in os.walk(source):
#                for file in files:
#                    source_file_path = os.path.join(folder_path, file)
#                    f_out.add(source_file_path)
#    f_out.close()
#    print("Tar-GZip: Time elapsed: %.2fs" % (time.time() - time_start), )
#
#
##benchmark_gzip(9)
##benchmark_bz2(9)
##benchmark_lzma()
##benchmark_tar_gzip()

###############################################################################

#def compress_encrypt():
#    time_start = time.time()
#    bytes_processed = 0
#    buffer_size = 8192 * 128
#    my_filters = [
#                  {"id": lzma.FILTER_DELTA, "dist": 5},
#                  {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME}
#                  ]
#    f_in_path = r"Y:\_TMP\bsTest\t2\1001292238015"
#    f_in = open(f_in_path, "rb")
#    f_out_path = r"Y:\_TMP\bsTest\t2\compressed_encrypted"
#    try:
#        os.remove(f_out_path)
#    except: pass
#    f_out = open(f_out_path, "ab")
#    compressor = lzma.LZMACompressor(check=lzma.CHECK_SHA256,
#                                     filters=my_filters)
#    iv = Crypto.Random.new().read(Crypto.Cipher.AES.block_size)
#    f_out.write(iv)
#    counter = Crypto.Util.Counter.new(128)
#    aes = Crypto.Cipher.AES.new("passwordpassword", Crypto.Cipher.AES.MODE_CTR, iv, counter)
#
#    while True:
#        data_raw = f_in.read(buffer_size)
#        if not data_raw:
#            break
#        data_compressed = compressor.compress(data_raw)
#        print(data_compressed[:2])
#        data_compressed_encrypted = aes.encrypt(data_compressed)
#        f_out.write(data_compressed_encrypted)
#
#        bytes_processed += buffer_size
#        time_elapsed = time.time() - time_start
#        print("%.1fs\t%s/s\t%s"
#              % (time_elapsed,
#                 bs.utils.formatDirSize(bytes_processed/time_elapsed),
#                 bs.utils.formatDirSize(bytes_processed) ))
#    f_out.write(compressor.flush())
#    print("Done: Compression & Encryption")
#
#
#def decompress_decrypt():
#    time_start = time.time()
#    bytes_processed = 0
#    buffer_size = 8192 * 128
#
#    f_in_path = r"Y:\_TMP\bsTest\t2\compressed_encrypted"
#    f_in = open(f_in_path, "rb")
#    f_out_path = r"Y:\_TMP\bsTest\t2\raw"
#    try:
#        os.remove(f_out_path)
#    except: pass
#    f_out = open(f_out_path, "ab")
#    decompressor = lzma.LZMADecompressor()
#
#    iv = f_in.read(Crypto.Cipher.AES.block_size)
#    counter = Crypto.Util.Counter.new(128)
#    aes = Crypto.Cipher.AES.new("passwordpassword", Crypto.Cipher.AES.MODE_CTR, iv, counter)
#    while True:
#        data_compressed_encrypted = f_in.read(buffer_size)
#        if not data_compressed_encrypted:
#            break
#        data_compressed = aes.decrypt(data_compressed_encrypted)
#        data_raw = decompressor.decompress(data_compressed)
#        print(data_raw[:2])
#        f_out.write(data_raw)
#
#        bytes_processed += buffer_size
#        time_elapsed = time.time() - time_start
#        print("%.1fs\t%s/s\t%s"
#              % (time_elapsed,
#                 bs.utils.formatDirSize(bytes_processed/time_elapsed),
#                 bs.utils.formatDirSize(bytes_processed) ))
#    print("Done: Decryption & Decompression")
#
#
#def lzma_compress():
#    time_start = time.time()
#    bytes_processed = 0
#    buffer_size = 8192 * 128  # 8192
#    my_filters = [
#                  {"id": lzma.FILTER_DELTA, "dist": 5},
#                  {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME}
#                  ]
#    try:
#        os.remove(r"Y:\_TMP\bsTest\t2\compressed")
#    except: pass
#    f_in = open(r"Y:\_TMP\bsTest\t2\1001292238015", "rb")
#    f_out = open(r"Y:\_TMP\bsTest\t2\compressed", "ab")
#    compressor = lzma.LZMACompressor(check=lzma.CHECK_SHA256,
#                                     filters=my_filters)
#    while True:
#        data_raw = f_in.read(buffer_size)
#        if not data_raw:
#            break
#        data_compressed = compressor.compress(data_raw)
#        f_out.write(data_compressed)
#
#        bytes_processed += buffer_size
#        time_elapsed = time.time() - time_start
#        print("%.1fs\t%s/s" % (time_elapsed, bs.utils.formatDirSize(bytes_processed/time_elapsed), ))
#    # write remaining buffer to f_out
#    f_out.write(compressor.flush())
#
#
#def encrypt():
#    time_start = time.time()
#    bytes_processed = 0
#    buffer_size = 8192 * 128  # 16
#    try:
#        os.remove(r"Y:\_TMP\bsTest\t2\compressed_encrypted")
#    except: pass
#
#    iv = Crypto.Random.new().read(Crypto.Cipher.AES.block_size)
#    counter = Crypto.Util.Counter.new(128)
#    aes = Crypto.Cipher.AES.new("passwordpassword", Crypto.Cipher.AES.MODE_CTR, iv, counter)
#    with open(r"Y:\_TMP\bsTest\t2\compressed", "rb") as f_in, open(r"Y:\_TMP\bsTest\t2\compressed_encrypted", "ab") as f_out:
#        f_out.write(iv)
#        while True:
##            plaintext = f_in.read(Crypto.Cipher.AES.block_size * 128)
#            plaintext = f_in.read(buffer_size)
#            print(plaintext[:2])
#            if not plaintext:
#                break
#            cipher = aes.encrypt(plaintext)
#            f_out.write(cipher)
#
#            bytes_processed += buffer_size
#            time_elapsed = time.time() - time_start
#            print("%.1fs\t%s/s" % (time_elapsed, bs.utils.formatDirSize(bytes_processed/time_elapsed), ))
#
#
#def decrypt():
#    time_start = time.time()
#    bytes_processed = 0
#    buffer_size = 8192 * 128  # 16
#    try:
#        os.remove(r"Y:\_TMP\bsTest\t2\compressed2")
#    except: pass
#    with open(r"Y:\_TMP\bsTest\t2\compressed_encrypted", "rb") as f_in, open(r"Y:\_TMP\bsTest\t2\compressed2", "ab") as f_out:
#        iv = f_in.read(Crypto.Cipher.AES.block_size)
#        counter = Crypto.Util.Counter.new(128)
#        aes = Crypto.Cipher.AES.new("passwordpassword", Crypto.Cipher.AES.MODE_CTR, iv, counter)
#        while True:
#            cipher = f_in.read(buffer_size)
#            if not cipher:
#                break
#            plaintext = aes.decrypt(cipher)
#            f_out.write(plaintext)
#
#            bytes_processed += buffer_size
#            time_elapsed = time.time() - time_start
#            print("%.1fs\t%s/s" % (time_elapsed, bs.utils.formatDirSize(bytes_processed/time_elapsed), ))
#
#
#def lzma_decompress():
#    time_start = time.time()
#    bytes_processed = 0
#    buffer_size = 1024 * 8  # 8192
#    try:
#        os.remove(r"Y:\_TMP\bsTest\t2\raw")
#    except: pass
#    f_in = open(r"Y:\_TMP\bsTest\t2\compressed2", "rb")
#    f_out = open(r"Y:\_TMP\bsTest\t2\raw", "ab")
#    decompressor = lzma.LZMADecompressor()
#
#    while True:
#        data = f_in.read(buffer_size)
#        if not data:
#            break
#        data_decompressed = decompressor.decompress(data)
#        f_out.write(data_decompressed)
#
#        bytes_processed += buffer_size
#        time_elapsed = time.time() - time_start
#        print("%.1fs\t%s/s" % (time_elapsed, bs.utils.formatDirSize(bytes_processed/time_elapsed), ))
#
#
#compress_encrypt()
##decompress_decrypt()
#lzma_compress()
#encrypt()
##decrypt()
##lzma_decompress()

###############################################################################

#from Crypto.Cipher import AES
#
#obj = AES.new("This is a key456", AES.MODE_CBC, "This is an IV456")
#message = "The answer is no"
#ciphertext = obj.encrypt(message)
#print(ciphertext)
#obj2 = AES.new("This is a key456", AES.MODE_CBC, "This is an IV456")
#ciphertext2 = obj2.decrypt(ciphertext)
#print(ciphertext2)

###############################################################################

###############################################################################
