from pubs.models import Publication, Member

# split this into functions
# add an error #

def check_pub_identifier(pub, issues):
    member_bib_num = pub.identifier.split(".")[0]

    # confirm that a member matching this bib number exists
    try:
        member_from_bib_num = Member.objects.get(bib_number=member_bib_num)

        # confirm that this member appears in members
        if member_from_bib_num not in pub.members.all():
            error = "Member indicated by bib number not present in members field"
            issues.append({pub.drupal_nid: error})
            # issues[pub.drupal_nid] = error

        # flag any members not accounted for in the bib number
        for member in pub.members.all():
            # convert to str because some bib_numbs are strings like "Unassigned"
            if str(member.bib_number) != str(member_bib_num):
                error = f"Non-matching bib number: expected {member_bib_num}, got {member.bib_number}"
                print(error)
                # issues[pub.drupal_nid] = error
                issues.append({pub.drupal_nid: error})

        # confirm that this member appears in creators
        member_in_creators = False
        for creator in pub.creators.all():
            if creator.label == member_from_bib_num.authority_record.heading:
                member_in_creators = True
        if not member_in_creators:
            error = f"Member {member_bib_num} does not appear in creators"
            # issues[pub.drupal_nid] = error
            issues.append({pub.drupal_nid: error})
    except:
        error = f"Member matching this bib number does not exist: {member_bib_num}"
        # issues[pub.drupal_nid] = error
        issues.append({pub.drupal_nid: error})


def search():
    issues = []

    for pub in Publication.objects.all():
        # for each member, see if bib number corresponds
        if pub.identifier:
            check_pub_identifier(pub, issues)

        # compare member and creator LCSH - have to do this for two members to two creators
        for member in pub.members.all():
            pass
        pass

    print(issues)