import os


def deleteFilesInFolder(path):
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))


def deleteAudioFiles():
    deleteFilesInFolder('./AudioFiles')
