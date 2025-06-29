
from django.shortcuts import render # type: ignore
from django.http import HttpResponse # type: ignore
import joblib
import numpy as np
import pandas as pd # Import pandas for CSV handling 
import io 

from django.contrib import admin # type: ignore

from mlmodelplatform import settings
from .models.signup import User_Detail

from django.core.files.storage import FileSystemStorage # type: ignore
import os

# below is for launching page
def home(request):
    print("hello hii i am karadiya haiderali")
    return render(request, "index.html")

def DATA(request):
    return render(request, "DATA.html")

def signup(request):
    return render(request, "signup.html")

# below for login logic
def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('usernameOrEmail')
        password = request.POST.get('password')

       
        user_detail = User_Detail.objects.filter(user_name=name).first()

        if user_detail:
            
            if user_detail.password == password: 
                company_name = user_detail.companyname 

                request.session['profile_name'] = name
                request.session['companyname'] = company_name 

                
                return render(request, 'HOME.html', {
                    'message_login': "LOGIN SUCCESSFULLY!",
                    'profile_name': name,
                    'companyname': company_name
                })
            else:
                
                return render(request, 'login.html', {'message_login_invalid': "! INVALID CREDENTIALS !"})
        else:
           
            return render(request, 'login.html', {'message_login_invalid': "! INVALID CREDENTIALS !"})
    return render(request, 'login.html')   


# below for signup
def userdata_view(request):
       
        is_license_authorized = False 
        
        if request.method == 'POST':
           
            company_name = request.POST.get('companyName')
            company_phone = request.POST.get('companyNo')
            email = request.POST.get('email')
            department = request.POST.get('department')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')
            profile_photo = request.FILES.get('profilePhoto') 
            license_image_file = request.FILES.get('licenseFile')

           
            request.session['profile_name'] = username
            request.session['companyname'] = company_name

          
            if password != confirm_password:
               
                return render(request, 'signup.html', {'is_license_authorized': is_license_authorized})
            
            if User_Detail.objects.filter(gmail=email).exists():
              
                return render(request, 'signup.html', {'is_license_authorized': is_license_authorized})
            
            if User_Detail.objects.filter(user_name=username).exists():
                
                return render(request, 'signup.html', {'is_license_authorized': is_license_authorized})
            
            try:
              
                if license_image_file:
                    fs_licenses = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_uploaded_licenses','original_licenses'))
                    
              
                    if not os.path.exists(fs_licenses.location):
                        os.makedirs(fs_licenses.location)

                    uploaded_filename = fs_licenses.save(license_image_file.name, license_image_file)
                    uploaded_file_path = os.path.join(fs_licenses.location, uploaded_filename)

                    default_license_path = os.path.join(settings.MEDIA_ROOT, 'default_licenses', 'default_license.jpg') 
                   
                    if os.path.exists(uploaded_file_path):
                        fs_licenses.delete(uploaded_filename)
                        print(f"Deleted temporary uploaded license: {uploaded_filename}")
                else:
                    is_license_authorized = False
                    request.session['license_authorized'] = False
                    print("No license file was uploaded by the user.")
                   
                hashed_password = password 
                
                user = User_Detail(
                    companyname=company_name,
                    companyphone=company_phone,
                    gmail=email,
                    department=department,
                    user_name=username,
                    password=hashed_password, 
                    image=profile_photo, 
                )
                user.save()

                
                return render(request,'HOME.html',{'message_signup':"ACCOUNT CREATED SUCCESFULLY"}) # Make sure 'HOME' is a valid URL name in your urls.py

            except Exception as e:
                return render(request, 'signup.html', {'is_license_authorized': is_license_authorized})
        return render(request, 'signup.html', {'is_license_authorized': is_license_authorized})

# below is just knownig that logout is there 
def about_logout(request):
    
    return render(request, "about_logout.html")

def login(request):
    return render(request, "login.html")


# real working logout working 
def logout(request):
     
     if 'profile_name' in request.session:
        print(f"Session before deletion: {request.session.items()}")
        del request.session['profile_name']
        del request.session['companyname']
        request.session['companyname'] = "Resign Guard"
        print("profile_name deleted from session.")
        print(f"Session after deletion: {request.session.items()}")
        request.session.save()  
        return render(request, "HOME.html", {
            'model_loaded': True,
            'message_logout': "successfully logged out!"
        })
    


# ----------------------------------BELOW IS CSV FILE IMPLEMENTATION------------------------------------------------

import os
import joblib
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse # Import HttpResponse 
import csv # Import csv module

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'working', 'model_files')

try:
    cat_model = joblib.load(os.path.join(MODEL_DIR, 'cat_model.pkl'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    label_encoders = joblib.load(os.path.join(MODEL_DIR, 'label_encoders.pkl'))
except FileNotFoundError as e:
    print(f"Error loading model files: {e}. Please ensure they are in {MODEL_DIR}")
    
    cat_model = None
    scaler = None
    label_encoders = None



# ✅ ADDITION: Load predictions_with_risk_factors
try:
    risk_factors_df = joblib.load(os.path.join(MODEL_DIR, 'predictions_with_risk_factors.pkl'))
except:
    risk_factors_df = None




def predict_csv(request):
    """
    Handles CSV file upload, prediction, and displays results.
    Also stores raw predicted data in session for download.
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        action = request.POST.get('action')  
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage()
        file_path = fs.save(csv_file.name, csv_file)
        full_path = fs.path(file_path)

        try:
            df = pd.read_csv(full_path)
        except Exception as e:
           
            return render(request, 'HOME.html', {'error_message': 'Invalid CSV file format. Please upload a valid CSV file.'})

        
        name_column = None
        if 'Name' in df.columns:
            name_column = df['Name'].copy()
            df = df.drop(columns=['Name']) 


        if action == 'view_original':
            # Display the original CSV content as an HTML table
            html_table = df.to_html(classes="table table-bordered", index=False)
            return render(request, 'HOME.html', {
                'original_table_html': html_table,
                'original_file_name': csv_file.name,
                'model_loaded': True 
            })


        elif action == 'predict':
            if cat_model is None or scaler is None or label_encoders is None:
                return render(request, 'HOME.html', {'error_message': 'Model files not loaded. Cannot perform prediction.'})

           
            for col, le in label_encoders.items():
                if col in df.columns:
                    try:
                       
                        df[col] = le.transform(df[col].astype(str))
                    except Exception:
                        return render(request, 'HOME.html', {'error_message': f'Encoding failed for column: {col}. Make sure all categories in the uploaded file are known to the model.'})

           
            try:
                df_scaled = scaler.transform(df)
            except Exception:
                return render(request, 'HOME.html', {'error_message': 'Scaling failed. Check your CSV columns and ensure they match the training data used for the model.'})

        
            probabilities = cat_model.predict_proba(df_scaled)[:, 1]  
            predictions = (probabilities >= 0.3).astype(int) 

            
            result_df = pd.DataFrame({
                'Attrition_Predicted': predictions,
                'Attrition_Probability': probabilities
            })



            # ADDITION: Add Key_Risk_Factor and Suggestion from precomputed DataFrame
            if risk_factors_df is not None and len(risk_factors_df) >= len(df):
                result_df['Key_Risk_Factor'] = risk_factors_df['Key_Risk_Factor'][:len(df)].values
                # result_df['Suggestion'] = risk_factors_df['Suggestion'][:len(df)].values
            else:
                result_df['Key_Risk_Factor'] = 'N/A'
                # result_df['Suggestion'] = 'N/A'





           


            if name_column is not None:
                result_df['Name'] = name_column
                
                result_df = result_df[['Name', 'Attrition_Predicted', 'Attrition_Probability', 'Key_Risk_Factor']]
            else:
               
                result_df = result_df[['Attrition_Predicted', 'Attrition_Probability', 'Key_Risk_Factor']]


            request.session['predicted_data_for_download'] = result_df.to_dict(orient='records')
            request.session['original_file_name'] = csv_file.name 
            request.session.modified = True 

            results_for_display = []
            for index, row in result_df.iterrows():
                row_dict = row.to_dict()
                prob = row_dict['Attrition_Probability']
                color = 'red' if prob >= 0.30 else 'green' 
                circle_html = f'<span style="height: 12px; width: 12px; background-color: {color}; border-radius: 50%; display: inline-block; margin-left: 5px;"></span>'
                
                row_dict['Attrition_Probability'] = f"{prob:.4f} {circle_html}"
                results_for_display.append(row_dict)
                
            return render(request, 'HOME.html', {
                'predicted_table_html': results_for_display, 
                'original_file_name': csv_file.name,
                'model_loaded': True 
            })

    
    return render(request, 'HOME.html', {'model_loaded': True})


def download_predicted_csv(request):
    """
    Retrieves predicted data from the session and serves it as a CSV file.
    """
 
    data = request.session.get('predicted_data_for_download', [])
    original_file_name = request.session.get('original_file_name', 'attrition_data')

    if not data:
        
        return HttpResponse("No predicted data found to download. Please upload a CSV and perform a prediction first.", status=404)

   
    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = f'attachment; filename="{original_file_name}_predictions.csv"'

    writer = csv.writer(response)

    if data:
        writer.writerow(data[0].keys())

    for row_dict in data:
        writer.writerow(row_dict.values())

    return response