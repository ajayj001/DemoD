from django.shortcuts import render
from django.views import generic
# Create your views here.
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponse
from .models import InputForm, Author, BookInstance, Genre, Book
from .compute import compute
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import  PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

from .forms import RenewBookForm


def index(request):
    """
    View function for home page of site
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances= BookInstance.objects.count()
    # Available books (status='a')

    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count() # the 'all()' is implied by default

    # Render the html template index.html with the data in the contxt variable

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,
            'num_visits':num_visits}, # num_visits appended
    )

class BookListView(generic.ListView):
    model= Book
    """
    context_object_name = 'my_book_list'   # your own name for the list as a template variable
    queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location
    """
    def get_queryset(self):
        #return Book.objects.filter(title__contains='')[:5] # Get 5 books containing the title war
        return Book.objects.all()
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    """
    Generic class-based list view for a list of authors.
    """
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """
    Generic class-based detail view for an author.
    """
    model = Author




from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name ='demo/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



class LoanedBooksAllListView(PermissionRequiredMixin,generic.ListView):
    """
    Generic class-based view listing all books on loan. Only visible to e to users with can_mark_returned permission.
    """
    model = BookInstance
    permission_required='demo.can_mark_returned'
    template_name='demo/bookinstance_list_borrowed_all.html'
    paginate_by=10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@permission_required('demo.can_mark_returned')
def renew_book_librarian(request,pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance,pk=pk)
    #if this ia POST request then process the form databases
    if request.method =='POST':
        # create the form instance
        form = RenewBookForm(request.POST)

        # Check igf the form is valid
        if form.is_valid():
            #process the data in form.cleaned_data
            book_inst.due_back= form.cleaned_data['renewal_date']
            book_inst.save()
            #
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date=datetime.date.today()+datetime.timedelta(weeks=3)
        form=RenewBookForm(initial={'renewal_date':proposed_renewal_date,})

    return render(request,'demo/book_renew_librarian.html',{'form':form,'bookinst':book_inst})


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    Author_det=[Author.objects.all()]

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
