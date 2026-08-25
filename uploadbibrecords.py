import csv
from pubs.models import Member, Subject, Creator, Publication, RELATOR_CHOICES
import re



def get_first_from_pipe_field(field):
    # for pipe-separated fields where DB can only currently handle one entry, split and return first item
    if "|" in field:
        return field.split("|")[0]
    else:
        return field

def get_year(field):
    # extract first year mentioned in year field, OR return None
    pattern = r"\d\d\d\d"
    match = re.search(pattern, field)

    if match:
        return match.group()
    else:
        return None
    
def add_subjects(input, publication):
    if input:
        subject_ids = input.split("|")
        for subject_id in subject_ids:
            try:
                subject = Subject.objects.get(drupal_tid=subject_id)
                publication.subjects.add(subject)
                # print(f"Added association with subject: {subject}")
            except:
                print(f"Subject could not be created: id {subject_id}")

def add_members(input, publication, nid):
    try:
        # takes a str of pipe-separated member IDs and adds those members to the appropriate object
        member_ids = input.split("|")
        for member_id in member_ids:
            member = Member.objects.get(drupal_nid=member_id)
            publication.members.add(member)
            # print(f"Added association with member: {member}")
    except:
        print(f"something went wrong while processing record: {nid}")
    return

# convert human-readable relator to relator code
# requires flipping key and value in RELATOR_CHOICES
def get_relator(input):
    relators_reversed = {}
    for k, v in RELATOR_CHOICES.items():
        relators_reversed[v] = k

    return relators_reversed[input]

def add_creators(name, uri, relators_all, publication):
    if uri:
        authority="LOC"
    else:
        authority="LCL"

    subject, created = Subject.objects.get_or_create(
        heading=name,
        uri=uri,
        authority_source=authority,
    )

    relators = relators_all.split("|")

    # in the case of multiple relators, add that creator multiple times
    for relator in relators:
        creator, created = Creator.objects.get_or_create(
            # TODO: pull this from subject instead
            label=name,
            subject=subject,
            relator=get_relator(relator),
        )

        publication.creators.add(creator)
        # print(f"Creator added: {creator}")

def upload_bib_record():
    with open("bib-records.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            publication, created = Publication.objects.get_or_create(
                identifier=row["bib_number"],
                editions_note=row["editions_note"],
                # holding_note=row["holding_note"],
                title=row["title"],
                year_published=get_year(row["year"]),
                publication=row["publication"],
                record_source=row["record_source"],
                references=row["references"],
                aps_record_link=get_first_from_pipe_field(row["aps_permalink"]),
                record_permalink=get_first_from_pipe_field(row["external_permalink"]),
                drupal_nid=row["nid"],
                annotator=get_first_from_pipe_field(row["created_by"]),
            )
            # if created:
            #     print(f"Created publication: {row["title"]}")

            add_subjects(row["subjects"], publication)
            add_subjects(row["aps_subjects"], publication)
            add_members(row["members"], publication, row["nid"])

            # add authority records for creator 1 and creator 2
            if row["creator_1_name"] and row["creator_1_relator"]:
                add_creators(row["creator_1_name"], row["creator_1_lcsh"], row["creator_1_relator"], publication)
            if row["creator_2_name"] and row["creator_2_relator"]:
                add_creators(row["creator_2_name"], row["creator_2_lcsh"], row["creator_2_relator"], publication)

            # except Exception as e:
            #     print(f"Something went wrong while saving member: {row['full_name']}")
            #     print(e)

def upload():
    upload_bib_record()