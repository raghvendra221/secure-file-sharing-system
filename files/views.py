from django.shortcuts import render,redirect
from .forms import FileUploadForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def home(request):
    return HttpResponse("Secure File Sharing System Running")

@login_required
def home(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            secure_file = form.save(commit=False)
            secure_file.owner = request.user
            secure_file.original_name = request.FILES['file'].name
            secure_file.save()
            return redirect('home')
    else:
        form = FileUploadForm()

    return render(request, 'files/upload.html', {'form': form})
