from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import  slugify
from django.db.models.signals import pre_save # right before the model save we gonna do something


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    creator = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('post_by_category', args=[self.name])

#Post.objects.all()
#Post.objects.create(user=user,title="some title")
class PostManager(models.Manager):
    def active(self,*args,**kwargs):
        #Post.objects.all() = super(PostManager,self).all()
        return super(PostManager,self).filter(draft=False).filter(published__lte=timezone.now())



class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,null=True,blank=True)
    content = models.TextField()
    image = models.ImageField(null=True,blank=True,upload_to='photos/%Y/%m/%d/')
    pub_date = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User,on_delete=models.CASCADE) #on_delete is required argument for ForeignKey, you should add it for all ForeignKey fields:
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    draft = models.BooleanField(default=False)
    published = models.DateField(auto_now=False,auto_now_add=False,default=timezone.now())

    objects = PostManager() # here the attribute objects name is just an arbitrary variable by convention we used this name

    def __str__(self): #to return a hard coded string
        return self.title

    def get_absolute_url(self): # to provide a link to a particular object or want to display that object's specific URL (if it has one) to the user
        return reverse('blog:postdetail', kwargs={'slug': self.slug})



class Comment(models.Model):
    content = models.TextField()
    by = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)


# def create_slug(instance, new_slug=None): # here instance is the object of a class which we will use in our function
#     slug = slugify(instance.title)
#     if new_slug is not None:
#         slug = new_slug
#     qs = Post.objects.filter(slug=slug).order_by("-id")
#     exists = qs.exists()
#     if exists:
#         new_slug = "%s-%s" %(slug, qs.first().id)
#         return create_slug(instance, new_slug=new_slug)
#     return slug



from .utils import unique_slug_generator

def pre_save_post_receiver(sender, instance, *args, **kwargs): # to make sure this function send every time when we create title or slug we need a sender signal to do so
    if not instance.slug: # if there is no slug present
        #instance.slug = create_slug(instance)
        instance.slug = unique_slug_generator(instance)



pre_save.connect(pre_save_post_receiver, sender=Post) # by signal pre save will run the function every time a model is created