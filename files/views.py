from django.shortcuts import render,redirect
from .utils import encrypt_with_key, decrypt_with_key, generate_file_key   
from .permissions import can_download, can_generate_token, can_upload, can_delete
from .forms import FileUploadForm, ShareTokenForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import FileShareToken, SecureFile
from datetime import timedelta
import secrets
from django.utils import timezone


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


@login_required
def generate_share_token(request, file_id):
    secure_file = get_object_or_404(SecureFile, id=file_id)

    if not can_generate_token(request.user, secure_file):
        return HttpResponseForbidden("Not allowed.")

    if request.method == "POST":
        form = ShareTokenForm(request.POST)
        if form.is_valid():
            expiry_minutes = form.cleaned_data['expiry_minutes']
            max_downloads = form.cleaned_data['max_downloads']

            token_string = secrets.token_urlsafe(32)

            expiry_time = timezone.now() + timedelta(minutes=expiry_minutes)

            FileShareToken.objects.create(
                file=secure_file,
                token=token_string,
                expiry_time=expiry_time,
                max_downloads=max_downloads
            )

            share_link = request.build_absolute_uri(
                f"/share/{token_string}/"
            )

            return render(request, "files/share_success.html", {
                "share_link": share_link
            })

    else:
        form = ShareTokenForm()

    return render(request, "files/generate_token.html", {
        "form": form,
        "file": secure_file
    })

@login_required
def token_download(request, token):

    if request.user.role != "viewer":
        return HttpResponseForbidden("Only viewers can access shared files.")

    share_token = get_object_or_404(FileShareToken, token=token)

    if not share_token.is_active:
        return HttpResponse("Token inactive.")

    if share_token.is_expired():
        share_token.is_active = False
        share_token.save()
        return HttpResponse("Token expired.")

    if share_token.current_downloads >= share_token.max_downloads:
        share_token.is_active = False
        share_token.save()
        return HttpResponse("Download limit reached.")

    # Increase download counter
    share_token.current_downloads += 1
    share_token.save()

    secure_file = share_token.file

    # Reuse your existing decryption logic here
    # (call your decrypt function and return file)

    return download_file(request, secure_file.id)