from django.shortcuts import render,redirect
from .utils import encrypt_with_key, decrypt_with_key, generate_file_key   
from .permissions import can_download, can_upload, can_delete
from .forms import FileUploadForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import SecureFile


@login_required
def home(request):
    if request.method == 'POST':
        if not can_upload(request.user):
            return HttpResponseForbidden("You are not allowed to upload files.")
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_data = uploaded_file.read()

            # Step 1: Generate per-file key
            file_key = generate_file_key()
            #encrypt the file data before saving
            encrypted_data = encrypt_with_key(file_data,file_key)
            #save the encrypted file manually
            secure_file = form.save(commit=False)
            secure_file.owner = request.user
            secure_file.original_name = uploaded_file.name


            # Step 3: Encrypt file_key using MASTER_KEY
            encrypted_file_key = encrypt_with_key(file_key, settings.SECRET_KEY[:32].encode())
            secure_file.encrypted_file_key = encrypted_file_key
            secure_file.save()

            #overwrite the file with encrypted data
            file_path = secure_file.file.path

            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            return redirect('home')
    else:
        form = FileUploadForm()
    files = SecureFile.objects.filter(owner=request.user)

    return render(request, 'files/upload.html', {
        'form': form,
        'files': files
    })


@login_required
def download_file(request, file_id):
    secure_file = get_object_or_404(SecureFile, id=file_id)
    if not can_download(request.user, secure_file):
        return HttpResponseForbidden("Not allowed to download.")

    # Read encrypted file
    with open(secure_file.file.path, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt file_key first
    decrypted_file_key = decrypt_with_key(
        secure_file.encrypted_file_key,
        settings.SECRET_KEY[:32].encode()
    )

    # Decrypt file
    decrypted_file = decrypt_with_key(encrypted_data, decrypted_file_key)

    response = HttpResponse(decrypted_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{secure_file.original_name}"'

    return response


from .permissions import can_delete

@login_required
def delete_file(request, file_id):
    secure_file = get_object_or_404(SecureFile, id=file_id)

    if not can_delete(request.user, secure_file):
        return HttpResponseForbidden("Not allowed.")

    secure_file.delete()
    return redirect("home")