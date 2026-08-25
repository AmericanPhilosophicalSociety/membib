import uploadbibrecords
import uploadmembers
import uploadsubjects

def uploadall():
    print("Uploading subjects...")
    uploadsubjects.upload()
    print("Uploading members...")
    uploadmembers.upload()
    print("Uploading bib records...")
    uploadbibrecords.upload()