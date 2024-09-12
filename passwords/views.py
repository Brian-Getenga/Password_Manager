from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Password
from .forms import PasswordForm
import random
import string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.core.mail import send_mail
from django.conf import settings
from .models import StoredFile, StoragePackage
from .forms import FileUploadForm, FileShareForm, UserForm, ProfileForm
from django.http import HttpResponse
from .forms import EditFileForm
from django.contrib.auth.models import User




@login_required
def update_file(request, file_id):
    file_instance = get_object_or_404(StoredFile, id=file_id)

    if request.method == 'POST':
        form = EditFileForm(request.POST, request.FILES, instance=file_instance)
        if form.is_valid():
            form.save()
            return redirect('file_detail', file_id=file_instance.id)  # Redirect to the file's detail page after saving
    else:
        form = EditFileForm(instance=file_instance)

    return render(request, 'passwords/edit_file.html', {'form': form, 'file': file_instance})

@login_required
def file_list(request):
    query = request.GET.get('q', '')
    file_type = request.GET.get('type', None)
    
    # Filter files by the logged-in user
    files = StoredFile.objects.filter(user=request.user)
    
    # Apply additional filters if any
    if file_type:
        files = files.filter(file_type=file_type)
    if query:
        files = files.filter(file__icontains=query)
    
    used_space = request.user.profile.storage_percentage
    available_space = 100 - used_space  # Example calculation, adjust as necessary

    return render(request, 'file_list.html', {
        'files': files,
        'query': query,
        'used_space': used_space,
        'available_space': available_space,
    })



@login_required
def edit_file(request, file_id):
    file = get_object_or_404(StoredFile, id=file_id, uploaded_by=request.user)

    if request.method == 'POST':
        form = EditFileForm(request.POST, instance=file)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = EditFileForm(instance=file)

    return render(request, 'edit_file.html', {'form': form})


@login_required
def print_file(request, file_id):
    file = get_object_or_404(StoredFile, id=file_id, uploaded_by=request.user)

    # Logic to handle different types of files
    if file.file_type == 'document':
        # Example logic for printing a document
        response = HttpResponse(file.file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{file.file.name}"'
        return response
    elif file.file_type == 'photo':
        # Example logic for printing a photo
        response = HttpResponse(file.file, content_type='image/jpeg')
        response['Content-Disposition'] = f'inline; filename="{file.file.name}"'
        return response
    else:
        # Other file types can be handled similarly
        return HttpResponse("Printing not supported for this file type.")

@login_required
def delete_file(request, file_id):
    if request.method == 'POST':
        file = get_object_or_404(StoredFile, id=file_id)
        file.delete()
        messages.success(request, "File deleted successfully.")
        return redirect('file_list')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('file_list')



@login_required
def share_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        recipient_username = request.POST.get('recipient')
        message = request.POST.get('message', '')

        # Get the file and check if the logged-in user owns it
        file = get_object_or_404(StoredFile, id=file_id)

        if file.user != request.user:
            messages.error(request, "You do not have permission to share this file.")
            return redirect('file_list')

        # Get the recipient user
        try:
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            messages.error(request, "Recipient username does not exist.")
            return redirect('file_list')

        # Share the file
        file.shared_with.add(recipient)
        messages.success(request, f"File shared successfully with {recipient_username}!")
        return redirect('file_list')

    return redirect('file_list')

@login_required
def shared_files(request):
    # Get the files shared with the current user
    files = StoredFile.objects.filter(shared_with=request.user)
    
    context = {
        'files': files,
    }
    
    return render(request, 'passwords/shared_files.html', context)

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            stored_file = form.save(commit=False)
            stored_file.user = request.user  # Assign the current logged-in user as the owner
            stored_file.file_size = stored_file.file.size  # Update the file size
            stored_file.save()  # Save the StoredFile instance
            
            messages.success(request, 'File uploaded successfully!')
            return redirect('file_list')  # Redirect to the file list view after successful upload
        else:
            messages.error(request, 'Failed to upload the file. Please try again.')
    else:
        form = FileUploadForm()

    return render(request, 'passwords/upload_file.html', {'form': form})

def bytes_to_gb(bytes):
    return bytes / (1024 ** 3)  # Convert bytes to gigabytes

@login_required
def file_list(request):
    file_type = request.GET.get('type')
    query = request.GET.get('q')

    if file_type:
        files = StoredFile.objects.filter(file_type=file_type)
    else:
        files = StoredFile.objects.all()

    if query:
        files = files.filter(file__icontains=query)

    # Calculate the total used space in GB
    used_space = bytes_to_gb(sum(file.file.size for file in StoredFile.objects.all()))
    available_space = 20 - used_space

    context = {
        'files': files,
        'query': query,
        'used_space': used_space,
        'available_space': available_space,
    }
    return render(request, 'passwords/file_list.html', context)

@login_required
def upgrade_storage(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        try:
            package = StoragePackage.objects.get(id=package_id)
            # Redirect to the checkout page with the selected package ID
            return redirect('checkout', package_id=package_id)
        except StoragePackage.DoesNotExist:
            messages.error(request, 'Selected package does not exist.')
            return redirect('upgrade_storage')
    else:
        packages = StoragePackage.objects.all()
        # Calculate storage limit in GB for each package and format as string
        for package in packages:
            package.storage_limit_gb = package.storage_limit / (1024 ** 3)
            package.storage_limit_gb_formatted = f"{package.storage_limit_gb:.2f}"
        
        return render(request, 'passwords/upgrade_storage.html', {'packages': packages})
    
@login_required
def checkout(request, package_id):
    try:
        package = StoragePackage.objects.get(id=package_id)
    except StoragePackage.DoesNotExist:
        messages.error(request, 'Selected package does not exist.')
        return redirect('upgrade_storage')

    if request.method == 'POST':
        # Handle payment logic here (redirect to PayPal or M-Pesa)
        payment_method = request.POST.get('payment_method')
        if payment_method == 'paypal':
            return redirect('paypal_payment', package_id=package.id)
        elif payment_method == 'mpesa':
            return redirect('mpesa_payment', package_id=package.id)
        else:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('checkout', package_id=package.id)

    return render(request, 'passwords/checkout.html', {'package': package})

@login_required
def checkout(request, package_id):
    try:
        package = StoragePackage.objects.get(id=package_id)
    except StoragePackage.DoesNotExist:
        messages.error(request, 'Selected package does not exist.')
        return redirect('upgrade_storage')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'paypal':
            return redirect('paypal_payment', package_id=package.id)
        elif payment_method == 'mpesa':
            return redirect('mpesa_payment', package_id=package.id)
        else:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('checkout', package_id=package.id)

    return render(request, 'passwords/checkout.html', {'package': package})

@login_required
def download_file(request, file_id):
    # Fetch the file object, ensuring it's either owned by or shared with the user
    file = get_object_or_404(StoredFile, id=file_id)
    if file.user == request.user or request.user in file.shared_with.all():
        response = HttpResponse(file.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        return response
    else:
        return HttpResponse("You do not have permission to download this file.", status=403)
    

@login_required
def file_detail(request, file_id):
    file = get_object_or_404(StoredFile, id=file_id)
    if file.user != request.user:
        return redirect('file_list')  # Redirect if file does not belong to the user
    return render(request, 'passwords/file_detail.html', {'file': file})


@login_required
def password_search(request):
    query = request.GET.get('q')
    if query:
        passwords = Password.objects.filter(user=request.user, website__icontains=query)
    else:
        passwords = Password.objects.filter(user=request.user)
    return render(request, 'passwords/password_list.html', {'passwords': passwords, 'query': query})


@login_required
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            photo = form.cleaned_data.get('photo')
            if photo:
                user.profile.photo = photo
                user.profile.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'passwords/register.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import StoredFile

@login_required
def profile(request):
    user = request.user
    files = StoredFile.objects.filter(user=user)
    
    # Calculate total file size in bytes
    total_size_bytes = sum(file.file_size for file in files)
    
    # Convert bytes to gigabytes
    total_size_gb = total_size_bytes / (1024 * 1024 * 1024)

    # Define storage limit in gigabytes (example: 10 GB)
    storage_limit_gb = 10
    
    # Calculate storage percentage
    storage_percentage = min((total_size_gb / storage_limit_gb) * 100, 100)

    if request.method == 'POST':
        u_form = UserForm(request.POST, instance=user)
        p_form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
    else:
        u_form = UserForm(instance=user)
        p_form = ProfileForm(instance=user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'total_size_gb': total_size_gb,
        'storage_percentage': storage_percentage,
    }
    return render(request, 'passwords/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'passwords/change_password.html', {
        'form': form
    })

@login_required
def password_list(request):
    passwords = Password.objects.filter(user=request.user)
    return render(request, 'passwords/password_list.html', {'passwords': passwords})

@login_required
def password_create(request):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            password = form.save(commit=False)
            password.user = request.user
            password.save()
            return redirect('password_list')
    else:
        form = PasswordForm()
    return render(request, 'passwords/password_form.html', {'form': form})

@login_required
def password_update(request, pk):
    password = get_object_or_404(Password, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PasswordForm(request.POST, instance=password)
        if form.is_valid():
            form.save()
            return redirect('password_list')
    else:
        form = PasswordForm(instance=password)
    return render(request, 'passwords/password_form.html', {'form': form})

@login_required
def password_delete(request, pk):
    password = get_object_or_404(Password, pk=pk, user=request.user)
    if request.method == 'POST':
        password.delete()
        return redirect('password_list')
    return render(request, 'passwords/password_confirm_delete.html', {'password': password})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('password_list')
    else:
        form = UserCreationForm()
    return render(request, 'passwords/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('password_list')
    else:
        form = AuthenticationForm()
    return render(request, 'passwords/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def password_search(request):
    query = request.GET.get('q')
    if query:
        passwords = Password.objects.filter(user=request.user, website__icontains=query)
    else:
        passwords = Password.objects.filter(user=request.user)
    return render(request, 'passwords/password_list.html', {'passwords': passwords, 'query': query})

@login_required
def generate_password(request):
    length = int(request.GET.get('length', 12))
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return render(request, 'passwords/generate_password.html', {'password': password})