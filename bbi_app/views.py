from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DriverProfile, DrivingTrip, DiscountHistory
from .forms import UserRegistrationForm, DriverProfileForm, TripUploadForm
from .utils.driving_analysis import analyze_driving_data
import pandas as pd
from datetime import datetime
from .models import *

def home(request):
    return render(request, "base.html")

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = DriverProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Create initial discount history
            DiscountHistory.objects.create(
                driver=profile,
                participation_discount=profile.participation_discount,
                driving_discount=profile.driving_discount,
                total_discount=profile.total_discount
            )
            
            login(request, user)
            return redirect('dashboard')
    else:
        user_form = UserRegistrationForm()
        profile_form = DriverProfileForm()
    
    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    try:
        profile = request.user.driverprofile
    except DriverProfile.DoesNotExist:
        return redirect('complete_profile')
    
    trips = DrivingTrip.objects.filter(driver=profile).order_by('-end_time')[:5]
    discount_history = DiscountHistory.objects.filter(driver=profile).order_by('-date')[:6]
    
    # Calculate metrics for dashboard
    total_trips = DrivingTrip.objects.filter(driver=profile).count()
    avg_score = DrivingTrip.objects.filter(driver=profile).aggregate(models.Avg('overall_score'))['overall_score__avg'] or 0
    
    context = {
        'profile': profile,
        'trips': trips,
        'discount_history': discount_history,
        'total_trips': total_trips,
        'avg_score': round(avg_score, 1),
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def upload_trip_data(request):
    if request.method == 'POST':
        form = TripUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                profile = request.user.driverprofile
                csv_file = request.FILES['trip_data']
                
                # Read CSV file
                df = pd.read_csv(csv_file)
                
                # Analyze driving data
                trip_data = analyze_driving_data(df)
                
                # Create DrivingTrip record
                trip = DrivingTrip(
                    driver=profile,
                    start_time=trip_data['start_time'],
                    end_time=trip_data['end_time'],
                    distance_miles=trip_data['distance_miles'],
                    average_speed=trip_data['average_speed'],
                    max_speed=trip_data['max_speed'],
                    hard_brakes=trip_data['hard_brakes'],
                    rapid_accelerations=trip_data['rapid_accelerations'],
                    night_driving=trip_data['night_driving'],
                    speed_score=trip_data['speed_score'],
                    braking_score=trip_data['braking_score'],
                    acceleration_score=trip_data['acceleration_score']
                )
                trip.save()
                
                # Record discount history
                DiscountHistory.objects.create(
                    driver=profile,
                    participation_discount=profile.participation_discount,
                    driving_discount=profile.driving_discount,
                    total_discount=profile.total_discount
                )
                
                messages.success(request, 'Trip data uploaded successfully!')
                return redirect('dashboard')
            
            except Exception as e:
                messages.error(request, f'Error processing trip data: {str(e)}')
    else:
        form = TripUploadForm()
    
    return render(request, 'trip_details.html', {'form': form})

@login_required
def trip_details(request, trip_id):
    try:
        trip = DrivingTrip.objects.get(id=trip_id, driver=request.user.driverprofile)
        return render(request, 'trip_details.html', {'trip': trip})
    except DrivingTrip.DoesNotExist:
        messages.error(request, 'Trip not found')
        return redirect('dashboard')
'''
@login_required
def profile(request):
    profile = request.user.driverprofile
    if request.method == 'POST':
        form = DriverProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = DriverProfileForm(instance=profile)
    
    return render(request, 'profile.html', {'form': form, 'profile': profile})
'''
@login_required
def profile(request):
    try:
        profile = request.user.driverprofile
        # Your existing profile view logic here
        return render(request, 'profile.html', {'profile': profile})
    except Exception as e:  # Catch specific exception: DriverProfile.DoesNotExist
        messages.warning(request, "Please complete your driver profile first")
        return redirect('complete_profile')
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DriverProfileForm  # You'll need to create this
from .models import DriverProfile

@login_required
def complete_profile(request):
    # Check if profile already exists
    if hasattr(request.user, 'driverprofile'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DriverProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = DriverProfileForm()
    
    return render(request, 'complete_profile.html', {'form': form})