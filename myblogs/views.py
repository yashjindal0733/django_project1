from django.shortcuts import render, reverse
from django.http import HttpResponse
from .models import blog_category, contact_info, SubscribedUser, blog_post,Comment
from .forms import Blog_Form, BlogPost_Form
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CommentForm
from django.utils import timezone 
# Create your views here.
@login_required(login_url='loginuser')
def home(request):
    x = blog_category.objects.all()
    
    return render(request, 'myblogs/home.html', {"category": x})

def contact(request):
    if request.method == 'GET':
        return render(request, 'myblogs/contact.html')
    elif request.method == 'POST':
        email = request.POST.get('user_email')
        message = request.POST.get('message')
        x = contact_info(u_email=email, u_message=message)
        x.save()
        return render(request, 'myblogs/contact.html', {'feedback': 'Your message has been recorded'})


def blog(request):
    # Extract the category from the request parameters
    category_name = request.GET.get('category')

    # If a category is provided, filter blog posts by that category, otherwise, get all blog posts
    if category_name:
        blogs = blog_post.objects.filter(blog_cat__blog_cat=category_name)
    else:
        blogs = blog_post.objects.all()

    p = Paginator(blogs, 3)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    return render(request, 'myblogs/blog.html', {"blogs": page_obj, "category": category_name})


def sub(request):
    if request.method == 'GET':
        return render(request, 'myblogs/sub.html')
    elif request.method == 'POST':
        email = request.POST.get('use_email')
        if SubscribedUser.objects.filter(u_email=email).exists():
            return render(request, 'myblogs/sub.html', {'feedback': 'Already Subscribed'})
        else:
            x = SubscribedUser(u_email=email)
            x.save()
            return render(request, 'myblogs/sub.html', {'feedback': 'Thank You for subscribing our page'})


def ck(request):
    x = BlogPost_Form()
    return render(request,'myblogs/ck.html',{"x":x})


def allblogs(request):
    y=blog_post.objects.all()
    return render(request,'myblogs/allblogs.html',{"y":y})


def blog_details(request, blog_id):
    # Get the blog post object
    obj = get_object_or_404(blog_post, pk=blog_id)

    if request.method == 'GET':
        # Increment the view count for GET requests
        z = obj.view_count
        z += 1
        obj.view_count = z
        obj.save()

    comments = obj.comments.all()
    new_comment = None  # Initialize new_comment to None by default

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = obj
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'myblogs/blog_details.html', {"obj": obj, 'comments':comments, 'new_comment': new_comment, 'comment_form': comment_form})

    
    
def loginuser(request):
    if  request.method == 'GET':
        return render(request,'myblogs/loginuser.html',{'form': AuthenticationForm()})
    else:
        a=request.POST.get('username')
        b=request.POST.get('password')
        user=authenticate(request, username=a, password=b)
        if user is None:
            return render(request,'myblogs/loginuser.html',{'form': AuthenticationForm(),'error': 'Invalid credentials'})
        else:
            login(request, user)
            return redirect('home')
        

def signupuser(request):
    if  request.method == 'GET':
        return render(request,'myblogs/signupuser.html',{'form': UserCreationForm()})
    else:
        a=request.POST.get('username')
        b=request.POST.get('password1')
        c=request.POST.get('password2')
        if b==c:
            #check whether user name is unique
            if (User.objects.filter(username = a)):
                return render(request, 'myblogs/signupuser.html',{'form': UserCreationForm(), 'error':'Username already exists Try again with different username'})
            else:
                user=User.objects.create_user(username = a, password =b)
                user.save()
                login(request,user)
                return redirect('home')

        else:
            #password 1 and 2 do not match
            return render(request, 'myblogs/signupuser.html',{'form': UserCreationForm(),'error':'Password Mismatch Try Again'})

def logoutuser(request):
    if request.method == 'GET':
        logout(request)
        return redirect('home')

def search(request):
    query = request.GET.get('q')
    results_posts = []
    results_categories = []

    if query:
        # Filter blog posts
        results_posts = blog_post.objects.filter(blog_name__icontains=query)

        # Filter blog categories
        results_categories = blog_category.objects.filter(blog_cat__icontains=query)

        

    return render(request, 'myblogs/search_results.html', {'results_posts': results_posts, 'results_categories': results_categories, 'query': query})

def add_like(request, blog_id):
    obj = get_object_or_404(blog_post, pk=blog_id)
    print (obj.like_count)
    y=obj.like_count
    y=y+1
    obj.like_count=y
    obj.save()
    return redirect('blog_details', obj.id)
    # return HttpResponse('obj')

def comment_view(request, pk):
    commentform = CommentForm()
    if request.method=='POST':
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            cd = commentform.cleaned_data
            print(cd)
            new_comment = commentform.save(commit=False)
            new_comment.post = blog_post.objects.get(pk=pk)
            new_comment.save()
        return HttpResponseRedirect(reverse('myblogs:blog_details', args=[pk]))
    return render(request, 'myapp/comment.html', {'commentform':commentform})
def add_comment(request, blog_id):
    post = get_object_or_404(blog_post, pk=blog_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.created_at = timezone.now()  # Add this line to save the current timestamp
            comment.save()
            return redirect('blog_details', blog_id=post.id)

def delete_comment(request, blog_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    return redirect( 'blog_details', blog_id=blog_id)

def edit_comment(request, blog_id, comment_id):
    # Retrieve the comment object
    comment = Comment.objects.get(id=comment_id)
    
    if request.method == 'POST':
        # Process the form submission
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog_details', blog_id=blog_id)
    else:
        # Populate the form with existing comment data
        form = CommentForm(instance=comment)
    
    return render(request, 'myblogs/edit_comment.html', {'form': form})
    
