import csv
from pubs.models import Member, Subject, Creator, Publication
import re


def handle_pipe_field(field):
    # for pipe-separated fields where DB can only currently handle one entry, split and return first item
    if "|" in field:
        return field.split("|")[0]
    else:
        return field

def get_members(input, publication):
    # takes a str of pipe-separated member IDs and adds those members to the appropriate object
    member_ids = input.split("|")
    for member_id in member_ids:
        member = Member.objects.get(drupal_nid=member_id)
        publication.members.add(member)
        print(f"Added association with member: {member}")
    return

def get_year(field):
    # extract first year mentioned in year field, OR return None
    pattern = r"\d\d\d\d"
    match = re.search(pattern, field)

    if match:
        return match.group()
    else:
        return None

def get_creator(name, lcsh, relator, publication):
    relators  = {
        'RCP': 'Addressee',
        'ANN': 'Annotator',
        'ARR': 'Arranger',
        'ART': 'Artist',
        'ATT': 'Attributed name',
        'AUT': 'Author',
        'COM': 'Compiler',
        'CTB': 'Contributor',
        'EDT': 'Editor',
        'EGR': 'Engraver',
        'ILL': 'Illustrator',
        'LBT': 'Librettist',
        'TRL': 'Translator',
    }
    try:
        subject, created = Subject.objects.get_or_create(
            heading=name,
            uri=lcsh,
        )

        creator, created = Creator.objects.get_or_create(
            # TODO: pull this from subject instead
            label=name,
            suject=subject,
            # TODO: change this to get actual value
            relator="AUT",
        )

        publication.creators.add(creator)
    except:
        print(f"An error occurred while adding creator: {name}")
    pass

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
                # SUBJECTS
                record_source=row["record_source"],
                references=row["references"],
                aps_record_link=handle_pipe_field(row["aps_permalink"]),
                record_permalink=handle_pipe_field(row["external_permalink"]),
                drupal_nid=row["nid"],
                annotator=handle_pipe_field(row["created_by"]),
            )
            # subjects
            # members
            # creators
            
            # try:
            #     publication, created = Publication.objects.get_or_create(
            #         identifier=row["bib_number"],
            #         editions_note=row["editions_note"],
            #         holding_note=row["holding_note"],
            #         title=row["title"],
            #         year_published=get_year(row["year"]),
            #         publication=row["publication"],
            #         # SUBJECTS
            #         record_source=row["record_source"],
            #         references=row["references"],
            #         aps_record_link=handle_pipe_field(row["aps_permalink"]),
            #         record_permalink=handle_pipe_field(row["external_permalink"]),
            #         drupal_nid=row["nid"],
            #         annotator=handle_pipe_field(row["created_by"]),
            #     )
            #     # handle subjects, members, creators
            # except Exception as e:
            #     print(f"Something went wrong while saving member: {row['full_name']}")
            #     print(e)

def upload():
    upload_bib_record()