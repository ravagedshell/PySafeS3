#!/usr/bin/env python

# PySafeS3 is a tool to encrypt data and upload it to S3.

# This file is responsible for the common functions
# and definitions used by other components of the PySafeS3
# client. For instance, this file may generate manifest
# files, perform math functions, etc.

# Author: ravagedshell <github.com/ravagedshell>

import os,hashlib,datetime,uuid,base64
from re import X
from datetime import datetime, timezone
from subprocess import Popen, PIPE

VERBOSITY = 'ALL'

# Given a dictionary containing output 
# and log messages, write the ouput to screen.
def writeOutput(basicmessage, fullmessage):
    match VERBOSITY:
        case 'ALL':
            print('MSG: ' + fullmessage + ' TIMESTAMP: ' + getTimestampUTC(datetime.timestamp(datetime.now())))
        case 'STANDARD':
            print('MSG: ' + basicmessage + ' TIMESTAMP: ' +  getTimestampUTC(datetime.timestamp(datetime.now())))
        case 'QUIET':
            return False
        case __:
            print('MSG: ' + basicmessage + ' TIMESTAMP: ' +  getTimestampUTC(datetime.timestamp(datetime.now())))
            
# Function to return a given value in Bytes
# Converts TB, GB, MB, KB to bytes
def getUnitSizeInBytes(size,unit):
    match unit:
        case 'TB':
            unitsInBytes = size * (1024 ** 4)
        case 'GB':
            unitsInBytes = size * (1024 ** 3)
        case 'MB':
            unitsInBytes = size * (1024 ** 2)
        case 'KB':
            unitsInBytes = size * (1024 ** 1)
        case __:
            unitsInBytes = size * (1024 ** 2)
    return int(unitsInBytes)

# Return an ISO 8601 UTC Timestamp
def getTimestampUTC(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    utc_datetime = dt.replace(tzinfo=timezone.utc)
    return datetime.isoformat(utc_datetime)


# Trim a string in either direction
# Start would remove a character from the front
# Anything else will return string in length given
def trimString(string, direction, length):
    if direction == 'start':
        return string[length:]
    else:
        return string[:length]

# Given a file, get its properties in a dictionary
# Type, Name, Size, Directory
def getFileProperties(path):
    if os.path.exists(path):
        file_properties = dict([
            ('DIRECTORY_PATH', os.path.dirname(path))
        ])
        if os.path.isdir(path):
            file_properties['TYPE'] = "directory"
        elif os.path.isfile(path):
            file_properties['TYPE'] = "file"
            file_properties['FILE_NAME'] = os.path.basename(path)
            file_properties['FILE_SIZE'] = os.path.getsize(path)
        return file_properties
    else:
        return False

# Generates the hash of a given file
# by reading it in 64KB increments
def getFileHash(path,hash):
    match hash:
        case "sha256":
            hash = hashlib.sha256()
        case "sha384":
            hash = hashlib.sha384()
        case "sha512":
            hash = hashlib.sha512()
        case __:
            hash = hashlib.sha256()
    with open(path,"rb") as file:
        for byte_block in iter(lambda: file.read(getUnitSizeInBytes(64,'KB')),b""):
            hash.update(byte_block)
    return hash.hexdigest()

# Given a directory, walk through each subdirectory
# and get a list of files and directories to run
# getFileProperties on; return array of dicts
def generateManifest(path):
    manifest = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            file_properties = getFileProperties(subdir + '/' + file)
            file_properties['S3_KEY'] = trimString(file_properties['DIRECTORY_PATH'],'start',1) + '/'
            fileuuid = uuid.uuid4()
            file_properties['UUID'] = str(fileuuid)
            file_properties['UNENCRYPTED_SHA256'] = getFileHash(subdir + '/' + file,'sha256')
            file_properties['BACKUP_STATUS'] = False
            file_properties['SCAN_TIMESTAMP'] = getTimestampUTC(datetime.timestamp(datetime.now()))
            manifest.append(file_properties)
    return manifest

# Delete a file
# Overwrite if overwrite is set
def wipeFile(path,overwrite,overwritemethod):
    if overwrite == 0:
        Popen(['rm', '-f', path])
        return True
    else:
        x = 0
        filesize = os.path.getsize(path)
        ddByteSize = 'bs=' + filesize
        ddOutputFile = 'of=' + path
        while overwrite <= x:
            if overwritemethod == 'random':
                Popen(['dd', 'if=/dev/urandom', ddByteSize, ddOutputFile])
            else:
                Popen(['dd', 'if=/dev/zero', ddByteSize, ddOutputFile])
            x+1
        Popen(['rm', '-f', path])
        return True

def parseManifest(path):
    print("this will do something..I think")


# Given a file and base64 encoded passphrase
# create an archive and pass it to GPG to encrypt
# Delete unencrypted archive after encrypting it.
# Add options for skipcompression (skip gzip, just encrypt)
def createArchive(file,base64secret,backupdirectory='None',armor=False,skipcompression=False):
    filepath = file['DIRECTORY_PATH'] + '/' + file['FILE_NAME']
    if backupdirectory != 'None':
        backuppath = backupdirectory.rstrip('/') + file['DIRECTORY_PATH'] 
        print ("Creating directory structure")
        if os.path.exists(backuppath):
            writeOutput('Path exists..moving on','Path: ' + backuppath +' succesfully found. Moving to archive file.')
        else:
            mkdir = Popen(['mkdir', '-p', backuppath])
            mkdir.wait()
            writeOutput('Path did not exist..created path..moving on','Path: ' + backuppath +' was not present. Succesfully created path. Moving to archive file.')
        gpg_output_filename = backuppath + '/' + file['FILE_NAME'] + '.tar.gz.gpg'
    else:
        backuppath = file['DIRECTORY_PATH']
        gpg_output_filename = file['DIRECTORY_PATH'] + '/' + file['FILE_NAME'] + '.tar.gz.gpg'
    b64decoded = base64.b64decode(base64secret)
    decodedstring = (str(b64decoded,'UTF-8')).rstrip('\n')
    writeOutput('Compressing file ' + file['FILE_NAME'],'File: ' + filepath + ' is being compress using command -czf piped to STDOUT.')
    tar = Popen(['tar', '-czf', '-', filepath, '--to-stdout' ], stdout=PIPE)
    writeOutput('Encrypting file ' + file['FILE_NAME'],'File: ' + filepath + ' is being encrypted using gpg and saved as ' + gpg_output_filename)
    if armor:
        gpg = Popen(['gpg', '-c', '--pinentry-mode', 'loopback','--cipher-algo', 'AES256', '--armor', '--passphrase', decodedstring, '--output', gpg_output_filename], stdin=tar.stdout)
    else:
        gpg = Popen(['gpg', '-c', '--pinentry-mode', 'loopback','--cipher-algo', 'AES256', '--passphrase', decodedstring, '--output', gpg_output_filename], stdin=tar.stdout)
    gpg.wait()
    if os.path.exists(gpg_output_filename):
        writeOutput('File was succesfully written. Calculating hash..','File: ' + gpg_output_filename + ' succesfully encrypted and written to disk. Moving to calculate hash.')
        file['ENCRYPTED_SHA256'] = getFileHash(gpg_output_filename,'sha384')
        file['BACKUP_DIRECTORY_PATH'] = backuppath
        file['BACKUP_FULL_PATH'] = gpg_output_filename
        file['BACKUP_FILENAME'] = file['FILE_NAME'] + '.tar.gz.gpg'
        file['ENCRYPTED_TIMESTAMP'] = getTimestampUTC(datetime.timestamp(datetime.now()))
        file['ENCRYPTED_FILESIZE'] = os.path.getsize(gpg_output_filename)
        return file
    else:
        writeOutput('File failed to write. Not sure what happened.','File: ' + gpg_output_filename + ' failed to be written to disk. Unsure of what occured.')