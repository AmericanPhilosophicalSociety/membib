import csv
from pubs.models import Member, Subject


def handle_pipe_field(field):
    # for pipe-separated fields where DB can only currently handle one entry, split and return first item
    if "|" in field:
        return field.split("|")[0]
    else:
        return field

def upload_member():
    with open("members.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                # get or create authority record for this member
                if row["lcsh_id"]:
                    authority="LOC"
                else:
                    authority="LCL"

                # search by heading THEN add URI and authority because subjects loaded in from subjects.csv don't have URIs attached, causing some member subject authorities to be created twice
                subject, created = Subject.objects.get_or_create(
                    heading=row['lcsh'],
                    # uri=row['lcsh_id'],
                    # authority_source=authority,
                )

                subject.uri = row['lcsh_id']
                subject.authority_source = authority
                subject.save()

                # if created:
                #     print(f"Subject created: {row['lcsh']}, authority: {authority}")

                annotator = handle_pipe_field(row["created_by"])

                member, created = Member.objects.get_or_create(
                    bib_number = row["bib_number"],
                    first_name = row["first_name"],
                    last_name = row["last_name"],
                    suffix = row["suffix"],
                    # some dates end with a ?, which causes an error
                    election_date=row["election_date"][:4],
                    office=row["office"],
                    # bio=row["bio"],
                    # bio="Default bio for testing purposes",
                    bio_note=row["bio_note"],
                    # upload_to is only triggered when uploading from a form or admin
                    image=f"images/{row['file_name']}",
                    image_alt_text=row["img_alt"],
                    note=row["note"],
                    annotator=annotator,
                    drupal_nid=row["nid"],
                    authority_record=subject,
                )
                # if created:
                #     print(f"Member created: {row['lcsh']}")
            except Exception as e:
                print(f"Something went wrong while saving member: {row['lcsh']}")
                print(e)

def upload():
    upload_member()