from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

def year_mod(the_year, mod, start):
    if the_year is None:
        return None
    return 1 + ((the_year - start - 1) // mod)


class NamedModelAbstractBase(models.Model):
	
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.id) + ", " + self.name

    class Meta:
        abstract = True


class SparseDate(models.Model):
	day = models.IntegerField(
		null=True,
		blank=True,
		validators=[MinValueValidator(1),MaxValueValidator(31)]
	)
	month = models.IntegerField(
		null=True,
		blank=True,
		validators=[MinValueValidator(1),MaxValueValidator(12)]
	)
	year = models.IntegerField(
		null=True,
		blank=True,
		validators=[MinValueValidator(0),MaxValueValidator(2000)]
	)

	def __str__(self):
		return ",".join([str(i) if i is not None else "" for i in [self.month,self.day,self.year]])

# Create your models here.
class SavedQuery(models.Model):
    """
    Used to store a query for later use in a permanent link.
    """

    ID_LENGTH = 8

    # This is the short sequence of characters that will be used when repeating
    # the query.
    id = models.CharField(max_length=ID_LENGTH, primary_key=True)
    # A hash string so that the query can be quickly located.
    hash = models.CharField(max_length=255, db_index=True, default='')
    # The actual query string.
    query = models.TextField()
    # Indicates whether this is a legacy query or a new JSON format query
    is_legacy = models.BooleanField(default=True)

    def get_link(self, request, url_name):
        """
        This method can be called directly in Views that need to have
        permanent linking functionality.
        :param request: The web request containing POST data that needs to be
        persisted.
        :param url_name: The URL name that is used to revert a permanent link
        URL as specified in the urls.py file.
        :return: A plain text response containing the link or an Http405 error.
        """
        self.query = request.POST.urlencode()
        self.save()
        link = ''.join([
            'https://' if request.is_secure() else 'http://',
            request.get_host(),
            reverse(url_name, kwargs={'link_id': self.id})])
        return HttpResponse(link, content_type='text/plain')

    def get_post(self):
        """
        Parse the stored query string and return a dict which is compatible
        with the original post that generated the permalink.
        :return: dict with stored POST data.
        """
        src = parse_qs(self.query, keep_blank_values=True)
        post = {}
        for name, value in list(src.items()):
            # This is an ugly HACK to detect entries which should be lists
            # even though there is only one entry in said list.
            # This method is now being deprecated as we move in with a JSON
            # backend/frontend-agnostic format that is much cleaner and
            # more flexible.
            if len(value) == 1 and set(
                    {'choice_field', 'select'}).isdisjoint(name):
                post[name] = value[0]
            else:
                post[name] = value
        return post

    def save(self, *args, preserve_id=False, **kwargs):
        q = self.query
        if not isinstance(q, bytes):
            q = q.encode('utf8')
        hash_object = hashlib.sha1(q)
        self.hash = hash_object.hexdigest()
        if not self.id or not preserve_id:
            pre_existing = list(
                SavedQuery.objects.filter(hash=self.hash).filter(
                    query=self.query))
            if len(pre_existing) > 0:
                self.id = pre_existing[0].id
                # No update to perform.
                return
        if not self.id:
            self.id = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits
            ) for _ in range(self.ID_LENGTH))
        super().save(*args, **kwargs)
