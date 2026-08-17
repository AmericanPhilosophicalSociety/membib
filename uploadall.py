import uploadbibrecords
import uploadmembers
import uploadsubjects

def uploadall():
    uploadsubjects.upload()
    uploadmembers.upload()
    uploadbibrecords.upload()