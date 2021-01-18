from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
from random import choice
from markdown2 import markdown
from . import util


# Search form in the sidebar
class SearchForm(forms.Form):
	search = forms.CharField(
		required=False,
		widget=forms.TextInput(attrs={"placeholder": "Search Encyclopedia"})
	)


# Forms in the create.html
class CreateForm(forms.Form):
	newtitle = forms.CharField(
		help_text = "Help Text",
		widget = forms.TextInput(attrs={"placeholder": "New Title"})
	)

	newcontent = forms.CharField(
		widget = forms.Textarea(attrs={"placeholder": "Start New Article Here..."})
	)


# Form in the edit.html
class EditForm(forms.Form):
	edittitle = forms.CharField(
		help_text = "Help Text",
		widget = forms.HiddenInput()
	)
	
	editcontent = forms.CharField(
		widget = forms.Textarea()
	)

# Search form exist in every pages
sidebarform = SearchForm()


# Home page
def index(request):
	print("index")
	return render(request, "encyclopedia/index.html", {
		 "entries": util.list_entries(),
		"sidebarform": sidebarform
	})


# Page for every entries
def browse(request, titlelink):
	content = util.get_entry(titlelink)
	print(titlelink)
	# If the entry .md exists in wiki/entries
	if content:
		content = markdown(content)
		print("browse1")
		return render(request, "encyclopedia/browse.html", {
			"title": titlelink,
			"content": content,
			"sidebarform": sidebarform
		})
	# If not, go to the error page
	else:
		print("broese2")
		return render(request, "encyclopedia/error.html", {
			"sidebarform": sidebarform,
			"errormsg": f"The page about \"{titlelink}\" does not exist."
		})


# If get a search query from the search form in the sidebar or by url 'search/'
def search(request):
	# If it's a POST
	if request.method == "POST":
		form = SearchForm(request.POST)
		# If the search query is valid
		if form.is_valid():
			search = form.cleaned_data["search"].lower()
			pages = util.list_entries()
			fit_pages = [page for page in pages if search in page.lower()]
			# No relevant characters match, go to the error page
			if len(fit_pages) == 0:
				print("search1")
				return render(request, "encyclopedia/error.html", {
					"sidebarform": sidebarform
				})
			# Pecfect match, go to the 
			elif len(fit_pages) == 1 and fit_pages[0].lower() == search:
				print("search2")
				url_found = reverse('browse', kwargs={"titlelink": fit_pages[0]})
				return HttpResponseRedirect(url_found)
			# Show the relevant entries
			else:
				print("search3")
				return render(request, "encyclopedia/search.html", {
					"sidebarform": sidebarform,
					"fit_pages": fit_pages
				})
		# If the search query is not valid, go to home page
		else:
			print("search4")
			url_index = reverse('index')
			return HttpResponseRedirect(url_index)
	# If it's not a POST, go to home page
	else:
		print("search5")
		url_index = reverse('index')
		return HttpResponseRedirect(url_index)


# Create the new entry
def create(request):
	# Go to the create.html
	if request.method == "GET":
		createform = CreateForm()
		print("create1")
		return render(request, "encyclopedia/create.html", {
			"sidebarform": sidebarform,
			"newpage": createform
		})
	# Post the create entry form in create.html
	elif request.method == "POST":
		form = CreateForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data["newtitle"]
			pages = util.list_entries()
			# If the entry already exists, go to error page
			if len([page for page in pages if page.lower() == title.lower()]) > 0:
				print("create2")
				return render(request, "encyclopedia/error.html", {
					"sidebarform": sidebarform,
					"errormsg": "The entry \"{title}\" already exists."
				})
			# If it is a new entry, save it and then go to the new entry page
			content = form.cleaned_data["newcontent"]
			util.save_entry(title, content)
			print("create3")
			url_create = reverse('browse', kwargs={"titlelink": title})
			return HttpResponseRedirect(url_create)
	# If not GET, POST methods, go to home page
	else:
		print("create4")
		url_index = reverse('index')
		return HttpResponseRedirect(url_index)


# Edit any entry pages
def edit(request):
	# If got a post from any entry pages, then go to the edit page
	if request.method == "POST":
		title = request.POST["title"]
		content = util.get_entry(title)
		editform = EditForm(initial = {
			"edittitle": title,
			"editcontent": content
		})
		print("edit1")
		return render(request, "encyclopedia/edit.html", {
			"title": title,
			"sidebarform": sidebarform,
			"editform": editform
		})
	# If not a post, go to home page
	else:
		print("edit2")
		url_index = reverse('index')
		return HttpResponseRedirect(url_index)


# After editing an entry, save the changes
def save(request):
	# If got a post, check the form is valid or not
	if request.method == "POST":
		editform = EditForm(request.POST)
		# If valid, then save
		if editform.is_valid():
			title = editform.cleaned_data["edittitle"]
			editcontent = editform.cleaned_data["editcontent"]
			util.save_entry(title, editcontent)
			url_edited = reverse('browse', kwargs={"titlelink": title})
			print("save1")
			return redirect(url_edited)
		# If not valid, go to home page
		else:
			print("save2")
			url_index = reverse('index')
			return redirect(url_index)
	# If it's not a post, go to home page
	else:
		print("save3")
		url_index = reverse('index')
		return redirect(url_index)

# The random link in the sidebar
def random(request):
	randomget = choice(util.list_entries())
	print(randomget)
	url_random = reverse('browse', kwargs={"titlelink": randomget})
	return redirect(url_random)

