# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .models import SensorData, Action, MCU
from .serializers import SensorDataSerializer, ActionSerializer, MCUSerializer
# from .views import MCUViewSet
from django.http import StreamingHttpResponse, JsonResponse
import json
import time
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from .models import User
import plotly.offline as opy  
import plotly.express as px
from django.db.models import Q
from IPython.display import HTML
import plotly.subplots as sp


# class TestPermission(permissions.BasePermission):
#     """
#     Simple permission class for testing purposes (not recommended for production).
#     """
#     def has_permission(self, request, view):
#         # Allow PUT requests for testing only
#         return request.method == 'PUT'
class MCUViewSet(viewsets.ModelViewSet):
    queryset = MCU.objects.all()
    serializer_class = MCUSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ['id', 'user']
    
    @csrf_exempt
    def update(self, request, pk=None):
        # Get the object instance based on the primary key (pk)
        sensor_data = self.get_object()
        # sensordata = SensorData.objects.filter(mcuId=mcu_id).latest('dateTime')
        # sensordata = SensorData.objects.filter(mcuId=mcu_id).latest('dateTime')

        # Update the model instance with data from the request body
        serializer = self.get_serializer(sensor_data, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        latest_sensor_data = SensorData.objects.filter(mcuId=sensor_data.id).latest('dateTime')

        # Create a new Action object
        action = Action.objects.create(
            sensorData=latest_sensor_data,
            waterPumpVal=request.data.get('waterPumpVal', False)  # Handle missing value
        )

        # Return a serialized response with the updated data
        return Response(serializer.data, status=HTTP_200_OK)
    # Permission check: Only authenticated users can access MCU data
        # permission_classes = [isAuthenticated]



class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ['mcuId']
    # Permission check: Only authenticated users can access sensor data
    # permission_classes = [IsAuthenticated]

class ActionViewSet(viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer

    # Permission check: Only authenticated users can perform actions
    # permission_classes = [IsAuthenticated]



def sse_stream(request, mcu_id):
    """
    Sends server-sent events to the clients.
    """
    def event_stream():
        while True:
            mcu = MCU.objects.get(pk=mcu_id)
            try:
                sensordata = SensorData.objects.filter(mcuId=mcu_id).latest('dateTime')
                mcu = MCU.objects.get(pk=mcu_id)
                data = {
                'soilMoisture': sensordata.soilMoisture,
                'temperature': sensordata.temperature,
                'humidity' : sensordata.humidity,
                'waterPumpVal': mcu.waterPumpVal,
                'threshold': mcu.threshold,
                'irrigationTime' : mcu.irrigationTime,
                'sleepingTime' : mcu.sleepingTime,
                'name':mcu.name,
                'dateTime': {'yyyy':sensordata.dateTime.year,
                             'mm':sensordata.dateTime.month,
                             'dd':sensordata.dateTime.day,
                             'h':sensordata.dateTime.hour,
                             'm':sensordata.dateTime.minute,
                             's':sensordata.dateTime.second,},
                # ... include other fields
                }
                
               
                yield f'data: {json.dumps(data)}\n\n'
            except SensorData.DoesNotExist:
                data = {
                    'waterPumpVal': mcu.waterPumpVal,
                    'threshold': mcu.threshold,
                    'irrigationTime' : mcu.irrigationTime,
                    'sleepingTime' : mcu.sleepingTime,
                    'name':mcu.name,
                    }
                yield f'data: {json.dumps(data)}\n\n'
            except Exception as e:
                yield f'data: {{ "error": "{str(e)}" }}\n\n'
            time.sleep(1)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

# def index(request):
#     return render(request, 'index.html')
def index(request, mcu_id=None):
    if mcu_id:
        # mcu = MCU.objects.get(pk=mcu_id)
        return render(request, 'index.html', {'mcuId': mcu_id})

    else:
        # Handle case where no MCU ID is provided (use default logic)
          # Replace with your logic to get default MCU
        return render(request, 'index.html')
    # ... rest of your view logic using mcu object

    


def auth_reset_pass(request):
    return render(request, 'auth-reset-pass.html')
def charts_morris(request):
    return render(request, 'charts-morris.html')
def live(request):
    return render(request, 'live.html')
# def login(request):
#     return render(request, 'login.html')
def page_403(request):
    return render(request, 'page-403.html')
def page_500(request):
    return render(request, 'page-500.html')
def page_blank(request):
    return render(request, 'page-blank.html')
# def register(request):
#     return render(request, 'register.html')
def settings(request):
    return render(request, 'settings.html')


# def ui_tables(request):
#     return render(request, 'ui-tables.html')
def ui_tables(request, mcu_id):
    if mcu_id:
        # mcu = MCU.objects.get(pk=mcu_id)
        return render(request, 'ui-tables.html', {'mcuId': mcu_id})

    else:
        # Handle case where no MCU ID is provided (use default logic)
        # Replace with your logic to get default MCU
        return render(request, 'index.html')
# def ui_forms(request):
#     return render(request, 'ui-forms.html')
def ui_forms(request, mcu_id):
    if mcu_id:
        # mcu = MCU.objects.get(pk=mcu_id)
        return render(request, 'ui-forms.html', {'mcuId': mcu_id})

    else:
        # Handle case where no MCU ID is provided (use default logic)
        # Replace with your logic to get default MCU
        return render(request, 'ui-forms.html')
    # ... rest of your view logic using mcu object

# register login logic 
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if not email:
            error_message = 'Email is required.'
        elif User.objects.filter(email=email).exists():
            error_message = 'Email already exists.'
        elif password1 != password2:
            error_message = 'Passwords don\'t match.'
        else:
            # Create user if no errors
            user = User.objects.create_user(email, password1)
            mcu = MCU(user=user,waterPumpVal=False,name='esp',threshold=30,irrigationTime=30,sleepingTime=10)
            mcu.save()
            # login(request, user)  # Log in the user automatically
            return redirect('login.html')  # Redirect to your desired page

        # If errors, render the registration page with error message
        return render(request, 'register.html', {'error_message': error_message})
    else:
        return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # user = User.objects.filter(email=email).first()
        # user = authenticate(email=email, password=password)
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            login(request, user)
            try:
                mcu = user.mcu_set.first() # Access the related MCU object through the user
                return render(request, 'index.html', {'mcuId': mcu.id , 'user': user})
            except MCU.DoesNotExist:
                # Handle case where user has no associated MCU
                return render(request, 'login.html', {'error': 'User has no associated MCU'})
        else:
            error_message = 'Invalid email or password.'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

# charts work 

# def read(request):
#     if request.method == 'GET':
#         date = request.GET.get('date')    
#         # date = request.GET['date']
#         # Retrieve date parameter

#         if not date:
#             return render(request, 'ui-tables.html')  
#         try:
#             date_obj = datetime.datetime.strptime(date, '%m/%d/%Y')
#             year = date_obj.year
#             month = date_obj.month
#             day = date_obj.day
#         except ValueError:
#             # Handle invalid date format errors (optional)
#             return Response({'error': 'Invalid date format'}, status=400)      
#         filters = Q(dateTime__year=int(year)) & Q(dateTime__month=int(month)) & Q(dateTime__day=int(day))

#         # Filter data based on date and potentially user (if authenticated)
#         data = SensorData.objects.filter(filters)
#         # if request.user.is_authenticated:
#         # data = data.filter(user=request.user)

#         # Prepare data lists
#         temperatures = []
#         humidities = []
#         soilMoistures = []
#         timestamps = []
        
#         for item in data:
#             temperatures.append(item.temperature)
#             humidities.append(item.humidity)
#             soilMoistures.append(item.soilMoisture)  # Assuming soilMoisture represents water temperature
#             timestamps.append(item.dateTime)
#         if(temperatures == [] or humidities == [] or soilMoistures == [] or timestamps == []):
#             data = {}
#             return render(request, 'login.html')
#         # Create traces (charts)
#         # changable ********************************

#         trace_temp = go.Scatter(
#             x=[t.strftime('%H:%M:%S') for t in timestamps],  # Format timestamps for x-axis
#             y=temperatures,
#             mode='lines',
#             name='Temp(°C)',
#         )

#         trace_humidity = go.Scatter(
#             x=[t.strftime('%H:%M:%S') for t in timestamps],
#             y=humidities,
#             mode='lines',
#             name='Humidity(%)'
#         )

#         trace_soilMoisture = go.Scatter(
#             x=[t.strftime('%H:%M:%S') for t in timestamps],
#             y=soilMoistures,
#             mode='lines',
#             name='soilMoisture(%)'
#         )


#         # Structure traces as datasets
#         data1 = [trace_temp]
#         data2 = [trace_humidity]
#         data3 = [trace_soilMoisture]
        

#         # Build figures
#         fig1 = go.Figure(data=data1)
#         fig2 = go.Figure(data=data2)
#         fig3 = go.Figure(data=data3)

#         # Combine figures into a subplot
#         figs = cf.subplots([fig1, fig2, fig3], shape=(2, 2))
#         figs['layout'].update(height=630, width=1250, title='Data For IOSeeds')
#         # changable ********************************
#         # Generate HTML div containing charts (using Plotly's offline functionality)
#         div = opy.plot(figs, auto_open=True, output_type='div')

#         data = {
#             'my_data': div
#         }
#         data_json = json.dumps(data)
#         return HttpResponse(data_json, content_type='application/json')
#     else :
#         return render(request, 'index.html')
def fields(request, mcu_id):
    if mcu_id:
        # mcu = MCU.objects.get(pk=mcu_id)
        return render(request, 'fields.html',{'mcuId':mcu_id})
    else:
        # Handle case where no MCU ID is provided (use default logic)
          # Replace with your logic to get default MCU
        return render(request, 'index.html')
    
def read(request, year, month, day,mcu_id):

        if not year or not month or not day or not mcu_id:
            return HttpResponse({'message': 'No data found for the given date'}, status=404)
        # Handle missing date
        filters = Q(mcuId=mcu_id) & Q(dateTime__year=year) & Q(dateTime__month=month) & Q(dateTime__day=day)
        print(f"Constructed filters: {filters}")
        data = SensorData.objects.filter(filters)
        print(f"Number of data points retrieved: {data.count()}")

        # Improve data handling (optional)
        if not data.exists():
            return render(request, 'ui-tables.html', {'graph':'<h2>no data found</h2>', 'mcuId': mcu_id})

        temperatures = [item.temperature for item in data]
        humidities = [item.humidity for item in data]
        soilMoistures = [item.soilMoisture for item in data]  # Assuming soilMoisture represents water temperature
        timestamps = [t.strftime('%H:%M:%S') for t in data.values_list('dateTime', flat=True)]

        # trace_temp = go.Scatter(
        #     # t.strftime('%H:%M:%S') for t in
        #     x=[ timestamps],  # Format timestamps for x-axis
        #     y=temperatures,
        #     mode='lines',
        #     name='Temp(°C)',
        # )
        
        # trace_humidity = go.Scatter(
        #     x=[timestamps],
        #     y=humidities,
        #     mode='lines',
        #     name='Humidity(%)'
        # )

        # trace_soilMoisture = go.Scatter(
        #     x=[timestamps],
        #     y=soilMoistures,
        #     mode='lines',
        #     name='soilMoisture(%)'
        # )


        # # Structure traces as datasets
        # data1 = [trace_temp]
        # data2 = [trace_humidity]
        # data3 = [trace_soilMoisture]
        

        # # Build figures
        # fig1 = go.Figure(data=data1)
        # fig2 = go.Figure(data=data2)
        # fig3 = go.Figure(data=data3)

        # # Combine figures into a subplot
        # figs = cf.subplots([fig1, fig2, fig3], shape=(2, 2))
        # figs['layout'].update(height=630, width=1250, title='Data For IOSeeds')
        # # changable ********************************
        # # Generate HTML div containing charts (using Plotly's offline functionality)
        # # div = opy.plot(figs, auto_open=True, output_type='div')
            # Create a line chart using Plotly Express (simpler syntax)
        # fig1 = px.line(x=timestamps, y=soilMoistures, title='Soil Moisture',labels={'x':'Time','y':'soil Moisture'})
        # fig1.update_layout(title={'font_size':15,'xanchor':'center','x':0.5})
        # fig1.update_traces(line_color='#00f0ff', line_width=2.5)
        # fig2 = px.line(x=timestamps, y=temperatures, title='temparature')

        # fig3 = px.line(x=timestamps, y=humidities, title='humidity')
        # figs = cf.subplots([fig1, fig2, fig3], shape=(3, 1))
        # figs['layout'].update(height=1630, width=1080,)
        fig1 = px.line(x=timestamps, y=soilMoistures, title='Soil Moisture', labels={'x':'Time', 'y':'Soil Moisture'})
        fig1.update_layout(title={'font_size':15,'xanchor':'center','x':0.5})
        fig1.update_traces(line_color='#66b3ff', line_width=2.5)

        fig2 = px.line(x=timestamps, y=temperatures, title='Temperature', labels={'x':'Time', 'y':'Temperature'})
        fig2.update_layout(title={'font_size':15,'xanchor':'center','x':0.5})
        fig2.update_traces(line_color='#ff5c33', line_width=2.5)

        fig3 = px.line(x=timestamps, y=humidities, title='Humidity', labels={'x':'Time', 'y':'Humidity'})
        fig3.update_layout(title={'font_size':15,'xanchor':'center','x':0.5})
        fig3.update_traces(line_color='#5bd75b', line_width=2.5)

        # Create subplots
        figs = sp.make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=("Soil Moisture", "Temperature", "Humidity"))

        # Add traces to the subplots
        figs.add_trace(fig1.data[0], row=1, col=1)
        figs.add_trace(fig2.data[0], row=2, col=1)
        figs.add_trace(fig3.data[0], row=3, col=1)

        # Update layout
        figs.update_layout(
            height=1630, 
            width=900,
            title_text="Environmental Data Over Time",
            title_x=0.5,
            title_font_size=20
        )

        # Update x-axis and y-axis for each subplot
        figs.update_xaxes(title_text="Time", row=3, col=1)
        figs.update_yaxes(title_text="Soil Moisture", row=1, col=1)
        figs.update_yaxes(title_text="Temperature", row=2, col=1)
        figs.update_yaxes(title_text="Humidity", row=3, col=1)

        # Update the overall layout for the subplots
        
        # fig.update_layout(
        # title={
        #     'font_size': 24,
        #     'xanchor': 'center',
        #     'x': 0.5
        # })
        # Convert the figure to a dictionary (suitable for JSON)
        # div = opy.plot(fig, auto_open=True, output_type='div')
        # data = {
        #                         'my_data':div
        #                 }
        context= {'graph' :opy.plot(figs, output_type='div',auto_open=True), 'mcuId' : mcu_id}
        # print(fig1.to_html())
        return render(request, 'ui-tables.html', context)
        # div =" <h1>.....plotlychart ......</h1>"
        # data = {
        #     'my_data': div
        # }
        # # data_json = json.dumps(data) , content_type='application/json', safe=False
        # return JsonResponse(chart,safe=False)

def get_related_mcus(request, mcu_id):
  if request.method == 'GET':
    # Access MCU data from the request body (adjust based on your request format)
    
    
    try:
      # Fetch the MCU object based on the received ID
      mcu = MCU.objects.get(pk=mcu_id)
      
      # Filter related MCUs based on the same user
      related_mcus = MCU.objects.filter(user=mcu.user)
      
      # Prepare a list of data to return (adjust as needed)
      related_mcu_data = [
          {'id': mcu.id, 'name': mcu.name} for mcu in related_mcus
      ]
    #   related_mcu_data.append({'id' : mcu.id,'name':mcu.name})
      return JsonResponse({'status': 'success', 'data': related_mcu_data})
    except MCU.DoesNotExist:
      return JsonResponse({'status': 'error', 'message': 'MCU not found'})
  else:
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_new_mcu(request,mcu_id):
    if (request.method == 'POST'):
        try:
            mcu = MCU.objects.get(pk=mcu_id)
            user = mcu.user
            new_mcu = MCU(user=user,waterPumpVal=False,name='esp',threshold=30,irrigationTime=30,sleepingTime=10)
            new_mcu.save()
            return render(request, 'fields.html',{'mcuId':mcu_id})
        except Exception as e:
            return render(request, 'fields.html', {'error_message': str(e)})

    else :
        return render(request, 'fields.html', {'error_message': 'not allowed request method'})
    