import csv
from pubs.models import Subject


def upload_aps_subject():
    with open("aps-subjects.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                subject, created = Subject.objects.get_or_create(
                    heading=row['title'],
                    authority_source='APS',
                    drupal_tid=row['nid']
                )
                if created:
                    print(f"Subject created: {row['title']}, authority: APS")
            except:
                print(f"Something went wrong while saving subject: {row['title']}")

def upload_subject():
    with open("subjects.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                # query loc-authorities
                # set authority to LOC or LCL based on whether heading validates or not
                subject, created = Subject.objects.get_or_create(
                    heading=row['heading'],
                    authority_source='LOC',
                    drupal_tid=row['nid']
                )
                if created:
                    print(f"Subject created: {row['heading']}, authority: LOC")
            except:
                print(f"Something went wrong while saving subject: {row['heading']}")

def upload():
    upload_aps_subject()
    upload_subject()