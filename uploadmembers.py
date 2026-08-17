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

                subject, created = Subject.objects.get_or_create(
                    heading=row['lcsh'],
                    uri=['lcsh_id'],
                    authority_source=authority,
                )
                # if created:
                #     print(f"Subject created: {row['lcsh']}, authority: {authority}")

                created_by = handle_pipe_field(row["created_by"])

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
                    # do logic for image here
                    image_alt_text=row["img_alt"],
                    note=row["note"],
                    created_by=created_by,
                    drupal_nid=row["nid"],
                    authority_record=subject,
                )
                if created:
                    print(f"Member created: {row['lcsh']}")
            except Exception as e:
                print(f"Something went wrong while saving member: {row['full_name']}")
                print(e)

def upload():
    upload_member()