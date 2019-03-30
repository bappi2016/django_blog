from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.views import View
from django.views.generic import ListView,DetailView,\
    CreateView,UpdateView,DeleteView,FormView #Generic editing views for editing content


from urllib.parse import quote_plus  # turns the url string into share string
from .models import Post,Comment,Category,User
from .forms import PostForm,CommentForm
from django.utils import timezone
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# class based view for Home

class Home(ListView): # listview - return list of object
    model = Post # The model that this view will display data for
    template_name = 'blog/home.html'
    context_object_name = 'posts' # Designates the name of the variable to use in the context.
    ordering = 'pub_date'
    paginate_by = 3



    def get_queryset(self): # here we will override this method to show only the post that is published not saved as draft
        # for search
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query)
            ).distinct()
        #return Post.objects.filter(published__lte=timezone.now())
        if self.request.user.is_superuser:
            return Post.objects.all()
        else:
            return Post.objects.filter(published__lte=timezone.now())




#views for displaying individual post
class PostDisplay(DetailView): # detailview return single object
    model = Post

    def get_object(self, queryset=None): # Returns the single object that this view will display.
        # now create a variable which will call the superclass to
        object = super(PostDisplay,self).get_object()#call the super() so as not to loose other functionalities offered by the original method.
        object.view_count += 1
        object.save()
        return object


   # """Insert and update the comments and form into the context dict."""
    def get_context_data(self, **kwargs): # show the comments of the corrosponding content
        # get the existing context from our superclass.
        context = super(PostDisplay, self).get_context_data(**kwargs)
        # """Insert all the corresponding comments of particular post into the context dict."""
        context['comments']= Comment.objects.filter(post=self.get_object()) # we added the comments into the context--
        context['form'] = CommentForm # """Insert the CommentForm into the context dict."""
        slug = self.kwargs.get(self.slug_url_kwarg)
        instance = get_object_or_404(Post,slug=slug)
        share_string = quote_plus(instance.content) # by share string we able to share our content
        context['share_string']=share_string
        return context


@method_decorator(login_required(login_url='login'),name='dispatch')
class PostComments(FormView): # to publish comment-  A view that displays a form. On error, redisplays the form with
    # validation errors; on success, redirects to a new URL.
    form_class = CommentForm
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse which will need a success url as an argument.
        form.instance.by = self.request.user # the logged in user 'by' is the attribute of the Comment model class - by whom the comment will published
        post = Post.objects.get(slug=self.kwargs['slug']) # get the current post
        form.instance.post = post
        form.save() # """If the form is valid, save the associated model."""
        return super(PostComments,self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:postdetail',kwargs={'slug':self.kwargs['slug']})

# Now display the detail post for browsers which only accept GET and POST for now.
class PostDetail(View):
    def get(self,request,*args,**kwargs): # FOR display the POST
        view = PostDisplay.as_view()
        return view(request,*args,**kwargs)

    def post(self,request,*args,**kwargs): # FOR display the post with comment form
        view = PostComments.as_view()
        return view(request,*args,**kwargs)





@method_decorator(login_required(login_url='login'),name='dispatch')
class Dashboard(View):
    def get(self,request,*args,**kwargs):
        view = Home.as_view(
            template_name = 'blog/admin_page.html',
            paginate_by = 4
        )
        return view(request,*args,**kwargs)

class UpdatePost(UpdateView):
    model = Post
    #form_class = PostForm
    fields = ('title', 'category', 'author', 'content', 'image','published','draft')
    template_name_suffix = '_update_form'

    def get_object(self): #get_object method of Django's SingleObjectMixin class.
        slug = self.kwargs.get('slug')  # look kwargs id in the urls  instead of default pk
        return get_object_or_404(Post, slug=slug)



class PostDelete(DeleteView): # View for deleting an object retrieved with self.get_object()
    #template_name = 'blog/article_delete.html'
    model = Post

    def get_object(self):
        slug = self.kwargs.get('slug')  # look kwargs slug in the urls  instead of default pk
        return get_object_or_404(Post, slug=slug)

    def get_success_url(self):
        return reverse('blog:home_view')

class PostCategory(ListView):
    model = Post
    template_name = 'blog/post_category.html'
    paginate_by = 3


    def get_queryset(self):#Returns the queryset that will be used to retrieve the object that this view will display.
        self.category = get_object_or_404(Category,pk=self.kwargs['pk']) # retrieve the individual category by its pk
        return Post.objects.filter(category=self.category) # filter the post with its corresponding category based on unique field- the self.category store the value of pk

    def get_context_data(self, **kwargs): #Returns context data for displaying the object.
        context = super(PostCategory, self).get_context_data(**kwargs)
        context['category']=self.category
        return context

class UserCategory(ListView):
    model = User
    template_name = 'blog/user_category.html'
    paginate_by = 2

    def get_queryset(self):#use get_queryset class method for filtering the list of record return
        # create a variable which will retrieve the pk of the corresponding author of the User model
        self.author = get_object_or_404(User,pk=self.kwargs['pk'])
        # Then return all the post with filter with that particular author which belong to that pk
        return Post.objects.filter(author=self.author)

    # override get_context_data() in order to pass additional context variables to the template
    def get_context_data(self, **kwargs):
        #  # Call the base implementation first to get the context
        context = super(UserCategory, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['author']=self.author # add a variable named "author" to the context
        return context

@method_decorator(login_required(login_url='login'), name='dispatch')
class CreatePost(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    #fields = ('title','category','author','content','image')
    def form_valid(self, form):# If the form is valid, save the associated model."""
        # This method is called when valid form data has been POSTed.
        form.instance.author = self.request.user # instance will get the current data or current form
        self.object= form.save()
        return super(CreatePost,self).form_valid(form) # initiate the super class with method and parameter