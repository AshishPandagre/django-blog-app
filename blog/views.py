from django.views import generic
from .models import Post, Subscribers, Comment
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
import random
from django.db.models import Q
import math
import json


def error_404(request, exception):
	data = {}
	response = render(request, 'blog/404.html', data)
	return response

def error_500(request, *args, **argv):
	return render(request, 'blog/404.html')

class PostList(generic.ListView):
	queryset = Post.objects.filter(status=1).order_by('-created_on')
	template_name = 'blog/blog.html'
	paginate_by = 4

	def get_queryset(self): # new
		query = self.request.GET.get('q', '')
		print('\n')
		query = ' '.join(query.split())

		if query == None or query == '':
			object_list = Post.objects.filter(status=1).order_by('-created_on')
		
		else:
			print('query = ', query)
			object_list = []
			for que in query.split():

				pos_list = Post.objects.filter(
					Q(title__icontains=que) | Q(description__icontains=que) | Q(tags__icontains=que),
					status=1
				).order_by('-created_on')
				
				object_list.extend(pos_list)
				print(object_list)

		return list(set(object_list))


def post_detail(request, slug):
	template_name = 'blog/post.html'

	post = get_object_or_404(Post, slug=slug, status=1)
	post.n_views += 1
	post.save()

	comments = Comment.objects.filter(post=post, active=True).order_by('-created_on')

	return render(request, template_name, {'post': post, 
											'comments': comments,
											})


def comment(request):
	# if request.method == "POST":
	name = json.loads(request.body)['comment-name']
	email = json.loads(request.body).get('comment-email', None)
	body = json.loads(request.body)['comment-body']
	slug = json.loads(request.body)['slug']

	try:
		post = Post.objects.get(slug=slug)
		c = Comment.objects.create(name=name, post=post, body=body, email=email)
		c.save()
		post.n_comments += 1
		post.save()

		data = {
			'name': c.name,
			'date': c.created_on.strftime("%Y-%m-%d %H:%M:%S"),
			'body': c.body,
			'n_comments': post.n_comments
		}
		response = HttpResponse(json.dumps(data))
		response.status_code = 200
	except Exception as e:
		response = HttpResponse(json.dumps({"error": str(e)}))
		response.status_code = 500

	return response


def subscribe(request):
	email = json.loads(request.body).get('email', "ashish@gmail.com")
	print("email received = ", email)

	try:
		if(Subscribers.objects.filter(email=email).exists()):
			status_code = 409
		else:
			s = Subscribers.objects.create(email=email)
			s.save()
			status_code = 200

	except Exception as e:
		print(str(e))
		status_code = 500

	response = HttpResponse(status=status_code)
	return response


def index(request):

	# post ranking system to detect popular posts of all time.

	posts = list(Post.objects.filter(status=1))

	view_comment_score = []
	post_list = []

	if len(posts) != 0:
		max_view = max(post.n_views for post in posts)
		max_comment = max(post.n_comments for post in posts)

		for i, post in enumerate(posts):
			print('\n'*2)
			print(post.title)
			score = (0.3+math.log10(10+post.n_views) / math.log10(10+max_view)) + (0.7+math.log10(10+post.n_comments) / math.log10(10+max_comment))
			print(score)
			view_comment_score.append(score)

		ranking_dict = dict(zip(posts, view_comment_score))
		ranking_dict = {k: v for k, v in sorted(ranking_dict.items(), key=lambda item: item[1], reverse=True)}

		print(ranking_dict)
		
		post_list = list(ranking_dict.keys())[:3]
		print(post_list)

	return render(request, 'blog/index.html', {'post_list' : post_list})


