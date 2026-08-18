from pubs.models import Publication, Member, Creator
import csv

# split this into functions
# add an error #

def check_bib_num(member_from_bib_num, pub, issues):
    # confirm that member appears in members, flag any members not referenced in bib number
    bib_num_in_members = False
    for member in pub.members.all():
        if member == member_from_bib_num:
            bib_num_in_members = True
        else:
            error = f"Member {member} (bib number {member.bib_number}) is referenced in this record but not accounted for in bib_number {member_from_bib_num.bib_number}"
            # issues[pub.drupal_nid] = error
            issues.append({"nid": pub.drupal_nid, "error": error, "error_num": 2})

    if not bib_num_in_members:
        error = f"Member {member} corresponding to bib number {member_from_bib_num.bib_number} not present in members field"
        issues.append({"nid": pub.drupal_nid, "error": error, "error_num": 3})
        # issues[pub.drupal_nid] = error

    # confirm that this member appears in creators
    member_in_creators(member_from_bib_num, pub, issues, "check_bib_num")

# take a member and search for it in a bib record's creators field
def member_in_creators(member, pub, issues, called_by):
    member_in_creators = False
    for creator in pub.creators.all():
        if creator.label == member.authority_record.heading:
            member_in_creators = True

    if not member_in_creators:
        if called_by == "search":
            error_num = 4
            error = f"Member {member} appears in members but not creators"
        else:
            error_num = 5
            error = f"Member {member} associated with bib number {member.bib_number} does not appear in creators"
        # issues[pub.drupal_nid] = error
        issues.append({"nid": pub.drupal_nid, "error": error, "error_num": error_num})

# take a creator and search for it in a bib record's members field
#TODO: need to first confirm that this creator IS a member
def creator_in_members(creator, pub, issues):
    try:
        # find member record matching this creator
        member_from_creator = Member.objects.get(authority_record__heading=creator.label)

        # check if that record appears in the publication's associated members
        if member_from_creator not in pub.members.all():
            error = f"Creator {creator} (member {member_from_creator.drupal_nid}) appears in creators but not members"
            # issues[pub.drupal_nid] = error
            issues.append({"nid": pub.drupal_nid, "error": error, "error_num": 6})
    except:
        pass

# match a bib number to a member
def get_member_from_bib_num(pub, issues):
    member_bib_num = pub.identifier.split(".")[0]

    try:
        member_from_bib_num = Member.objects.get(bib_number=member_bib_num)
    except:
        error = f"Member matching this bib number does not exist: {member_bib_num}"
        # issues[pub.drupal_nid] = error
        issues.append({"nid": pub.drupal_nid, "error": error, "error_num": 1})
        member_from_bib_num = None

    return member_from_bib_num

def search():
    issues = []

    for pub in Publication.objects.all():
        # check that bib number corresponds to a member
        member_from_bib_num = get_member_from_bib_num(pub, issues)

        # if bib number corresponds to a member, check that that member is present in members and creators
        if member_from_bib_num:
            check_bib_num(member_from_bib_num, pub, issues)

        # confirm that each associated member appears in creators
        for member in pub.members.all():
            member_in_creators(member, pub, issues, "search")

        # confirm that each associated creator appears in members
        for creator in pub.creators.all():
            creator_in_members(creator, pub, issues)

    with open("weirdmemberdata.csv", "w", newline="", encoding="utf8") as csvfile:
        fieldnames = ["nid", "error", "error_num"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)