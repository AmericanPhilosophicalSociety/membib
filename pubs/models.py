from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django_edit_away.models import TiptapField


ANNOTATORS = {
    'AM': 'Alex Mazzaferro',
    'JA': 'Jeff Appelhans',
    'EMJ': 'Unknown EMJ',
    'AV': 'Unknown AV',
    'JF': 'Julie Fisher',
    'CP': 'Unknown CP',
    'SB': 'Unknown SB',
    'YS': 'Yumi Shiroma',
    'GS': 'Unknown GS',
    'CF': 'Unknown CF',
}


def validate_year(value):
    """Ensure that years entered are plausible"""
    current_year = datetime.now().year
    if value < 1700 or value > current_year:
        raise ValidationError(
            ('%(value)s does not match the expected date scope for this project'),
            params={'value': value},
        )


def verify_latlon(value):
    """Proxy validation for latitude and longitude that checks whether
    value is a decimal value between -180 and 180."""
    if not -180 <= value <= 180:
        raise ValidationError(
            'Latitude or longitude must be between -180 and 180 degrees.'
        )


class Subject(models.Model):
    AUTHORITY_CHOICES = {
        'APS': 'American Philosophical Society',
        'LOC': 'Library of Congress',
        'LCL': 'Local',
    }

    # Question: should this save the URL or just the ID?
    uri = models.CharField(max_length=20, blank=True, null=True)
    heading = models.CharField(max_length=200)
    authority_source = models.CharField(choices=AUTHORITY_CHOICES, max_length=3)
    drupal_tid = models.PositiveIntegerField(blank=True, null=True, editable=False)

    # for complex subjects
    components = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='component_of'
    )

    class Meta:
        ordering = ['heading']

    def __str__(self):
        return self.heading


class Member(models.Model):
    # even with these settings, DB won't accept an empty string value - not sure what's going on here. added temp bib IDs for the people still missing them to get the upload to work
    bib_number = models.PositiveIntegerField(blank=True, null=True, default=None)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    suffix = models.CharField(max_length=50, blank=True)
    # this should actually validate dates for the project, but oh well
    election_date = models.PositiveIntegerField(validators=[validate_year])
    office = models.CharField(max_length=100, blank=True)
    bio = TiptapField(blank=True, null=True)
    bio_note = models.TextField(blank=True)
    # Once DB is set up, set this to default to a the generic image to reduce storage redundancy
    image = models.ImageField(upload_to='images', default='default.jpg')
    image_alt_text = models.CharField(max_length=255)
    # is this field public facing?
    note = models.TextField(blank=True)
    # need to remediate to allow multiples
    created_by = models.CharField(max_length=3, choices=ANNOTATORS, blank=True)
    drupal_nid = models.PositiveIntegerField(blank=True, null=True, editable=False)
    authority_record = models.ForeignKey(Subject, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.suffix}"


class Creator(models.Model):
    RELATOR_CHOICES = {
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
    # this should be pulled from subject__heading probably
    label = models.CharField(max_length=200)
    # require this?
    subject = models.ForeignKey(
        Subject, blank=True, null=True, on_delete=models.PROTECT
    )
    # TODO: Implement relator more robustly - probably requires loc-authorities patch
    # this should accept multiple values
    relator = models.CharField(choices=RELATOR_CHOICES, max_length=3)
    def __str__(self):
        return self.label


class Publication(models.Model):
    RECORD_SOURCE_CHOICES = {
        'AAS': 'American Antiquarian Society',
        'APS': 'American Philosophical Society',
        'BNF': 'Bibliothèque nationale de France',
        'CORN': 'Cornell Uniersity Library',
        'ESTC': 'English Short Title Catalogue',
        'FOUNDERS': 'Founders Online',
        'HARV': 'Harvard Library',
        'HSP': 'Historical Society of Pennsylvania',
        'HUNT': 'The Huntington',
        'JCB': 'John Carter Brown Library',
        'LCP': 'Library Company of Philadelphia',
        'LOC': 'Library of Congress',
        'NBY': 'The Newberry',
        'NLM': 'National Library of Medicine',
        'NYHS': 'The New York Historical',
        'NYPL': 'New York Public Library',
        'PENN': 'University of Pennsylvania Libraries',
        'PU': 'Princeton University Library',
        'WC': 'Worldcat',
        'YALE': 'Yale Library',
        'NONE': 'None',
    }

    identifier = models.CharField(max_length=50)
    editions_note = models.TextField(blank=True)
    holding_note = TiptapField(blank=True, null=True)
    members = models.ManyToManyField(Member)
    creators = models.ManyToManyField(Creator)
    title = models.TextField()
    year_published = models.PositiveIntegerField(validators=[validate_year], blank=True, null=True)
    publication = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject)
    record_source = models.CharField(choices=RECORD_SOURCE_CHOICES, max_length=10)
    # revise this field
    references = models.CharField(max_length=255, blank=True)
    aps_record_link = models.URLField(null=True, blank=True)
    record_permalink = models.URLField()
    drupal_nid = models.PositiveIntegerField(blank=True, null=True, editable=False)
    # TODO: This needs to accept multiple values somehow
    annotator = models.CharField(choices=ANNOTATORS, max_length=3)

    def __str__(self):
        return self.title[:100]


class Edition(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    number_of_editions = models.PositiveIntegerField()
    year = models.PositiveIntegerField(validators=[validate_year])
    place_name = models.CharField(max_length=50)
    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        blank=True,
        null=True,
        validators=[verify_latlon],
    )
    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        blank=True,
        null=True,
        validators=[verify_latlon],
    )

    # TODO: Add method for querying external service to retrieve coordinates
