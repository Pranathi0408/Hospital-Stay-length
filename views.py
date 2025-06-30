import joblib
import numpy as np
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from sklearn.preprocessing import LabelEncoder

# Load the saved model, scaler, and LabelEncoder
model = joblib.load('et_model.pkl')  # Replace with your model file
scaler = joblib.load('scaler.pkl')  # Replace with your scaler file
label_encoder = joblib.load('label_encoder.pkl')  # Replace with your actual label encoder file

# Home view
def home(request):
    return render(request, 'home.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('predict_hospital_stay')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'login.html')

# Register view
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        if not all([username, password, email, first_name, last_name]):
            messages.error(request, "Please fill in all fields.")
            return redirect('register')
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            return redirect('register')
    return render(request, 'register.html')

# Predict hospital stay view
def predict_hospital_stay(request):
    if not request.user.is_authenticated:
        return redirect('login')

    prediction_text = None
    error_message = None

    if request.method == 'POST':
        try:
            # Retrieve input values from the form, ensuring they are valid
            location = request.POST.get('location', '')
            time = request.POST.get('time', '')
            mri_units = request.POST.get('mri_units', '')
            ct_scanners = request.POST.get('ct_scanners', '')
            hospital_beds = request.POST.get('hospital_beds', '')

            # Check if all fields are provided
            if not all([location, time, mri_units, ct_scanners, hospital_beds]):
                raise ValueError("All fields are required")

            # Convert inputs to the appropriate data types
            location = int(location)
            time = int(time)
            mri_units = float(mri_units)
            ct_scanners = float(ct_scanners)
            hospital_beds = float(hospital_beds)

            

            # Prepare the input data
            input_data = np.array([[location, time, mri_units, ct_scanners, hospital_beds]])

            # Scale the input data using the loaded scaler
            input_data_scaled = scaler.transform(input_data)

            # Make the prediction using the trained model
            prediction = model.predict(input_data_scaled)
            predicted_days = prediction[0]

            # Round the predicted days to the nearest integer
            predicted_days_int = int(round(predicted_days))

            # Provide a descriptive output
            if predicted_days_int > 5:
                stay_type = "Long length of stay"
            else:
                stay_type = "Short length of stay"

            # Pass prediction information to template
            prediction_data = {
                'days': predicted_days_int,
                'stay_type': stay_type
            }

            return render(request, 'prediction_result.html', {'prediction': prediction_data})

        except ValueError as e:
            error_message = f"Invalid input: {e}"
        except Exception as e:
            error_message = f"An error occurred: {e}"

    return render(request, 'prediction_form.html', {'error': error_message})


# Logout view
def logout_view(request):
    auth_logout(request)
    return redirect('login')
