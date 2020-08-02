from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from rest_framework import viewsets, filters, status, permissions, generics
from rest_framework.response import Response
from etwsystems.serializers import UserSerializer, GroupSerializer, MenusSerializer, ResSerializer, RestSerializer,CatSerializer, ResPostSerializer, CustomerSerializer,CustomerSerializer2,  OrderSerializer, OrderSerializer2
from etwsystems.models import Menus, Restaurants, Categories, Orders, Customer, OrderDetails
from etwsystems.forms import RestaurantsForm
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
# from .forms import BookingForm, RoomForm, DateForm, RoomtypeForm
from datetime import datetime, date, timedelta
from django.shortcuts import get_object_or_404
import random, requests, json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework_gis.filters import DistanceToPointFilter
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance  
from django.contrib.gis.geos import GEOSGeometry
from django.core import serializers
import stripe, base64, decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.core.mail import EmailMultiAlternatives     


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MenusViewSet(viewsets.ModelViewSet):
    queryset = Menus.objects.all()
    serializer_class = MenusSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)    
    def filter_queryset(self, queryset):
        queryset = super(MenusViewSet, self).filter_queryset(queryset)
        return queryset.order_by('-itemprice')

class ResViewSet(viewsets.ModelViewSet):
    queryset = Restaurants.objects.all()
    serializer_class = ResSerializer 
    permission_classes = (IsAuthenticatedOrReadOnly,)

class RestViewSet(viewsets.ModelViewSet):
    queryset = Restaurants.objects.all()
    serializer_class = RestSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)    


class CatViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('resno','categoriesno')
    queryset= Categories.objects.all()
    serializer_class = CatSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def filter_queryset(self, queryset):
        queryset = super(CatViewSet, self).filter_queryset(queryset)
        return queryset.order_by('rankno')


class MenusViewSetRes(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('categoriesno','resno', 'hidden')
    queryset= Menus.objects.all()
    serializer_class = MenusSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
# def datas(request):

class restpos(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = ResPostSerializer

class Customerviewset(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class Orderviewset(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('orderno','itemno')
    queryset = OrderDetails.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

class LocationList(viewsets.ModelViewSet):
    queryset = Restaurants.objects.all()
    serializer_class = ResSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def get_queryset(self):
        qs = super().get_queryset()
        latitude = self.request.query_params.get('lat',None)
        longitude =self.request.query_params.get('lng', None)
        distance=self.request.query_params.get('dis', None)

        if latitude and longitude and distance:
            pnt = Point(float(latitude), float(longitude))
            qs=Restaurants.objects.filter(location__distance_lt=(pnt, Distance(km=distance)))

            print(qs)
            return qs

        else:
            return None



@api_view(['POST'])
@permission_classes((AllowAny,))
def restpost(request):

    # if request.method == 'GET':
    #     serializer = ResPostSerializer
    #     return Response(serializer.data)
    # authentication_classes = (SessionAuthentication)
    if request.method == 'POST':
        serializer = ResPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            test = request.data['resno']
            test3 = Restaurants.objects.get(resno=1).rescode
            test2 = test
            # values = request.data
            values = {'rescode': test3}
            print(test3)

            headers =  {'content-type': 'application/json'}
            r=requests.post('http://####:3100/', data=json.dumps(values), headers=headers)
            t=r.text
            # print(r.text)

            return Response (serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes((AllowAny,))
def custom(request):

    if request.method == 'POST':
        serializer =CustomerSerializer2(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response (serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes((AllowAny,))
def orderin(request):
    # if request.method == 'GET':
    #     serializer = ResPostSerializer
    #     return Response(serializer.data)
    # authentication_classes = (SessionAuthentication)
    if request.method == 'POST':

        test4 = request.data
        var1 = test4['text']
        var2 = test4['orderno']
        var3 = test4['customerno']

        if  var1 == var2 + var3:
            now=datetime.now()
            asdf =  test4['orderno']
            if asdf != "11030":
                test4['orderrefno'] = asdf
            else:
                nowdate = now.strftime("%Y-%m-%d")
                today1 = Orders.objects.filter(orderdate=nowdate).count()
                test4['orderrefno'] = today1 + 1                

            test4['orderno']=now.strftime("%Y%d%m%H%M%S")+var3
            orderno = test4['orderno']
            test4['orderdate']=now.strftime("%Y-%m-%d")
            test4['gst'] = format(decimal.Decimal(test4['orderamount'])/decimal.Decimal(11),'.2f')





            serializer = ResPostSerializer(data=test4)



            if serializer.is_valid():   
                serializer.save()       
                # test = request.data['resno']
                # test3 = Restaurants.objects.get(resno=1).rescode
                # test2 = test
                # # values = request.data
                # values = {'rescode': test3}
                # # print(test3)

                # headers =  {'content-type': 'application/json'}
                # r=requests.post('http://####:3100/', data=json.dumps(values), headers=headers)
                # t=r.text
                # print(r.text)

                return HttpResponse(orderno)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    



@api_view(['POST'])
@permission_classes((AllowAny,))
def orderitem(request):
    # if request.method == 'GET':
    #     serializer = ResPostSerializer
    #     return Response(serializer.data)
    # authentication_classes = (SessionAuthentication)
   
    if request.method == 'POST':

        test1 = request.data
        itemno = test1['itemno']
        resno = test1['resno']
        orderno = test1['orderno']
        res = Restaurants.objects.get(resno=resno)
        sockid= res.rescode
        itemname = Menus.objects.get(itemno=itemno)
        name = itemname.itemname

        serializer = OrderSerializer2(data=request.data)
        print(request.data)
        if serializer.is_valid():

            serializer.save()       
            print(serializer)

            # values={'name':orderno, 'socketid': sockid }
            # headers =  {'content-type': 'application/json'}
            # r=requests.post('http://####:3001/', data=json.dumps(values), headers=headers)
                # test = request.data['resno']
                # test3 = Restaurants.objects.get(resno=1).rescode
                # test2 = test
                # # values = request.data
                # values = {'rescode': test3}
                # # print(test3)

                # headers =  {'content-type': 'application/json'}
                # r=requests.post('http://####:3100/', data=json.dumps(values), headers=headers)
                # t=r.text
                # print(r.text)
            return Response (serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   


@api_view(['POST'])
@permission_classes((AllowAny,))
def orderend(request):

    if request.method == 'POST':

        test0 = request.data
        orderno = test0['orderno']
        resno = test0['resno']
        res = Restaurants.objects.get(resno=resno)        
        sockid= res.rescode
     
        order = Orders.objects.get(orderno=orderno)
        orderrefno = order.orderrefno
        comments = order.comments
        customerno = order.customerno.phone_number
        time1=order.ordertime.strftime('%H:%M:%S')
        order.orderscompleted = True
        orderamount = "{:.2f}".format(order.orderamount)
        ordertype = order.ordertype
        order.save()

        values={'name':orderno, 'socketid': sockid, 'customerno':customerno, 'price':orderamount, 'orderno':orderrefno, 'time':time1 , 'ordertype':ordertype, 'comments':comments}
        headers =  {'content-type': 'application/json'}
        r=requests.post('http://####:3001/', data=json.dumps(values), headers=headers) 
            

        return HttpResponse(orderrefno)

    return HttpResponse('error')


# @csrf_exempt
# def detail(request):
#     if request.method == "POST":
#         values={'test':'test', 'socketid':'7720C3GHjDDObXf_AAAA'}
#         headers =  {'content-type': 'application/json'}
#         r=requests.post('http://####:3001/', data=json.dumps(values), headers=headers)
#         t=r.text
#         print(r.text)
#         return HttpResponse(t)

#     template = loader.get_template('eatapp/index.html')
   
#     return HttpResponse(template.render(request))		


# @csrf_exempt
# def detail(request):
#     order = Orders.objects.all()
#     if request.method == "POST":
#         stripe.api_key = "####"
#         acct = stripe.Account.create(
#         country="AU",
#         type="custom")
#         id1 = acct.id

#         return HttpResponse(id1)   

#     template = loader.get_template('eatapp/index.html')
   
#     return HttpResponse(template.render(request))   


@csrf_exempt
def detail(request):
    order = Orders.objects.all()
    if request.method == "POST":
        order.delete()

    template = loader.get_template('eatapp/index.html')
    # if request.method=="POST":
    #     items123 = Menus.objects.filter(resno=1)
    #     for a in items123:
    #         a.itemprice=format(decimal.Decimal(a.itemprice)*decimal.Decimal(1.02),'.2f')
    #         a.save()




    return HttpResponse(template.render(request))     







# @csrf_exempt
# def rng(request):
# 	if request.method =="GET":

# 		a = 

# 	return HttpResponse(x)


def registerrest(request):
    
    form = RestaurantsForm(request.POST or None, request.FILES or None) 
    if request.method == "POST":

        if form.is_valid():

            az=handle_uploaded_image(request.FILES['image'])
            location = request.POST.get('address')

            apikey = "AIzaSyALTo9xC0mWqSTLDvBHcpC6Tf00ARnI3Sc"

            url = "http://maps.google.com/maps/api/geocode/json?key="+ apikey + "address=" + str(location)
            now = datetime.today()

            aa  = form.save(commit=False)
            aa.last_modified_date = now 
            aa.rescode="1" 
            aa.image = az
            aa.save()

            url2 = "pk=" + str(aa.pk) + "&location="+ str(location)
            return redirect('/registerrest2/?%s' % url2)


    # template = loader.get_template('eatapp/index.html')
   
    # return HttpResponse(template.render(request))     

    context = {
         "form":form
    }
    return render(request, "eatapp/registrationform.html", context)



def handle_uploaded_image(i):
    # resize image
    import hashlib
    from django.core.files import File
    from django.core.files.uploadedfile import InMemoryUploadedFile
    thumbImage = Image.open(i)
    thumbImage = thumbImage.resize((400,300))
    thumbImage1 = File(thumbImage)
    thumb_io = BytesIO()
    thumbImage.save(thumb_io, format='JPEG')

    filename =  hashlib.md5(i.name.encode("utf8")).hexdigest()+'.jpg' 
    thumb_file = InMemoryUploadedFile(thumb_io, None, filename, 'image/jpeg',
                                  thumb_io.tell(), None)


    return (thumb_file)





def registerrest2(request):
    apikey = "AIzaSyALTo9xC0mWqSTLDvBHcpC6Tf00ARnI3Sc"

    pk = request.GET.get('pk')
    address1= request.GET.get('location')
    if not address1:
        asdf = 1
    else:
        asdf =0
    url = "https://maps.google.com/maps/api/geocode/json?key="+ apikey + "&address=" + str(address1)
    r = requests.get(url)
    t = r.json()
    lat = t['results'][0]['geometry']['location']['lat']
    lng = t['results'][0]['geometry']['location']['lng']

    address=str(lat) + ","+ str(lng)

    if request.method == "GET":
        url2 = "pk=" + str(pk) + "&location="+ str(address1)
        redirect('/registerrest2/?%s' % url2)
    if request.method == "POST":
        if form.is_valid():
            return redirect('registerrest2')


    # template = loader.get_template('eatapp/index.html')
   
    # return HttpResponse(template.render(request))     

    context = {
        "asdf":asdf,
        "apikey":apikey,
        "address":address,
        "pk":pk
    }
    return render(request, "eatapp/registrationform2.html", context)













def checkuser(request):
    if request.method == "GET":
        customerno = request.GET.get('caa')
        if not customerno:
            return HttpResponse('error')
        try:
            customerno = Customer.objects.get(customerno=customerno)
        except Customer.DoesNotExist:
            return HttpResponse('error')

        return HttpResponse('OK')

    return HttpResponse('error')    


@csrf_exempt
def updatecode(request):
    if request.method == "POST":
        # code = request.POST.get('code')
        # pw = request.POST.get('password')
        # sockid = request.POST.get('id')
        data=json.loads(request.body.decode('utf-8'))
        code = data['code']
        pw = data['password']
        sockid = data['id']
        print(pw)
        print(code)
        resta = Restaurants.objects.get(resno=code)
        restaname = resta.name

        if resta.respassword == pw:
            resta.rescode=sockid
            resta.connected=True
            resta.save()
            return HttpResponse('Welcome ' + restaname )
        else:
            return HttpResponse('error')

    return HttpResponse('error')      


@api_view(['GET'])
@permission_classes((AllowAny,))
def getorders(request):
    if request.method == "GET":
        resno = request.GET.get('resno')
        now =datetime.today()
        dt = datetime.now().time()
        d1 = now - timedelta(hours=1)
        # roq = request.META.get('HTTP_{ROQ}')
        # restaurant = Restaurants.objects.get(rescode=roq)
        # r = restaurant.resno

        details1 = Orders.objects.filter(orderdate=now)
        details = details1.filter(resno= resno)
        # details1 = details.filter(ordertime__gte=d1)
        list=[]
        for row in details:
            time=(row.ordertime).strftime('%H:%M:%S')
            orderamount = "{:.2f}".format(row.orderamount)
            orderss = OrderDetails.objects.filter(orderno=row.orderno)
            orderlist = []
            for a in orderss: 
                orderlist.append({'itemname':a.itemno.itemname,'quantity':int(a.quantity)})
            
            list.append({'ordertype':row.ordertype,'customerno':row.customerno.phone_number,'ordertime':time,'price':orderamount, 'orderrefno':row.orderrefno, 'pk':row.orderno, 'comments':row.comments,'items':orderlist})
        # data = serializers.serialize('json', list(details1), fields=('ordertype', 'Customer__phone_number','orderamount', 'ordertime'))
        list_json = json.dumps(list)
        return HttpResponse(list_json, 'application/javascript')






@api_view(['GET'])
@permission_classes((AllowAny,))
def getorders2(request):
    if request.method == "GET":
        resno = request.GET.get('resno')
        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')

        std = datetime.strptime(startdate,'%d-%m-%Y')
        end = datetime.strptime(enddate, '%d-%m-%Y')
        # dt = datetime.now()
        d1 = std - timedelta(hours=1)
        d2 = end- timedelta(hours=1)
        # roq = request.META.get('HTTP_{ROQ}')
        # restaurant = Restaurants.objects.get(rescode=roq)
        # r = restaurant.resno

        details1 = Orders.objects.filter(orderdate__gte=d1,orderdate__lt=d2)
        details = details1.filter(resno= resno)
        # details1 = details.filter(ordertime__gte=d1)
        list=[]
        for row in details:
            time=(row.ordertime).strftime('%H:%M:%S')
            orderamount = "{:.2f}".format(row.orderamount)
            orderss = OrderDetails.objects.filter(orderno=row.orderno)
            orderlist = []
            for a in orderss: 
                orderlist.append({'itemname':a.itemno.itemname,'quantity':int(a.quantity)})
            
            list.append({'ordertype':row.ordertype,'customerno':row.customerno.phone_number,'ordertime':time,'price':orderamount, 'orderrefno':row.orderrefno, 'pk':row.orderno, 'comments':row.comments,'items':orderlist})
        # data = serializers.serialize('json', list(details1), fields=('ordertype', 'Customer__phone_number','orderamount', 'ordertime'))
        list_json = json.dumps(list)
        return HttpResponse(list_json, 'application/javascript')




@api_view(['GET'])
@permission_classes((AllowAny,))
def getcust(request):
    if request.method == "GET":
        cust = request.GET.get('cust')
        pw = request.GET.get('qop')
        if pw == "31":
            today = datetime.now()
            cust = Orders.objects.filter(customerno = cust)

            reaa = cust.filter(orderdate__gte=today)
            data = serializers.serialize('json', list(reaa), fields=('orderrefno'))
        # roq = request.META.get('HTTP_{ROQ}')
        # restaurant = Restaurants.objects.get(rescode=roq)
        # r = restaurant.resno
            # response = JsonResponse(reaa, safe=False)

            return HttpResponse(data)
        return HttpResponse('error')         
    return HttpResponse('error') 



@api_view(['POST'])
@permission_classes((AllowAny,))
def handshake(request):
    if request.method == "POST":
        data=json.loads(request.body.decode('utf-8'))
        dd = data['handshake']
        ee = data['socket']
        try:
            thisres = Restaurants.objects.get(rescode=ee)
            if dd == "dc":
                thisres.connected=False
                thisres.save()
 
        except Restaurants.DoesNotExist:
            return HttpResponse('Error')


@api_view(['POST'])
@permission_classes((AllowAny,))
def remov(request):
    if request.method == "POST":
        data=json.loads(request.body.decode('utf-8'))
        dd = data['itemno']
        ee = data['qq']
        if ee == "1533833":
            try:
                thisitem = Menus.objects.get(itemno=dd)

                if thisitem.hidden is True:
                    thisitem.hidden = False
                    print("false")
                    thisitem.save()
                    return HttpResponse('ok')

                else:
                    thisitem.hidden = True
                    thisitem.save()
                    return HttpResponse('ok')
                return HttpResponse('ok')


     
            except Menus.DoesNotExist:
                return HttpResponse('Error')
        else:
            return HttpResponse('error')




@api_view(['GET'])
@permission_classes((AllowAny,))
def updateboolean(request):
    if request.method == "GET":
        verss = request.GET.get('v')
        p = request.GET.get('p')
        if verss == "1.4.0":
            if p=="ios":
                return HttpResponse('OK')
            if p =="and":
                return HttpResponse('OK')
            return HttpResponse('OK')        
        elif verss == "1.3.0":
            if p=="ios":
                return HttpResponse('https://play.google.com/store/apps/details?id=com.ionicframework.etws786779')
            if p =="and":
                return HttpResponse('https://play.google.com/store/apps/details?id=com.ionicframework.etws786779')        
        
            return HttpResponse('https://play.google.com/store/apps/details?id=com.ionicframework.etws786779')
        else:
            if p=="ios":
                return HttpResponse('https://play.google.com/store/apps/details?id=com.ionicframework.etws786779')
            if p =="and":
                return HttpResponse('https://play.google.com/store/apps/details?id=com.ionicframework.etws786779')  
        
    return HttpResponse('error')



@api_view(['POST'])
@permission_classes((AllowAny,))
def paymentgate(request):
    if request.method =="POST":
        test1=request.data
        stripe.api_key = "####"
        token = test1['stripeToken']
        customerno=test1['customerno']
        amt = test1['amt']

        try:
            customerno = Customer.objects.get(customerno=customerno)


            try:
                charge = stripe.Charge.create(
                    amount=amt,
                    currency="aud",
                    source=token,
                    transfer_group="ORDER42",
                )
                print("success")
                return HttpResponse('OK')
            except stripe.error.CardError as e:
                return HttpResponse('Card Error')
            except stripe.error.RateLimitError as e:
                return HttpResponse('Error, too many request')

            except stripe.error.InvalidRequestError as e:
                return HttpResponse('Invalid parameters error')

            except stripe.error.AuthenticationError as e:
              # Authentication with Stripe's API failed
              # (maybe you changed API keys recently)
                return HttpResponse('client authentication error')
            except stripe.error.APIConnectionError as e:
              # Network communication with Stripe failed
                return HttpResponse('network error')
            except stripe.error.StripeError as e:
              # Display a very generic error to the user, and maybe send
              # yourself an email
                return HttpResponse('Stripe error')
            except Exception as e:
              # Something else happened, completely unrelated to Stripe
                return HttpResponse('Unknown error')


        except Customer.DoesNotExist:
            return HttpResponse('error')



@api_view(['GET'])
@permission_classes((AllowAny,))
def checkstatus(request):
    if request.method =="GET":
        resno = request.GET.get('resno')
        try: 
            restatus = Restaurants.objects.get(resno=resno)
            status = restatus.connected
            return HttpResponse(status)
        except Restaurants.DoesNotExist:
            return HttpResponse('error')



@csrf_exempt

def paypalapi(request):
    if request.method =="GET":



        code3 = request.GET.get('code')

        # msg.send()

        string33 = ('####')
        encoded42= bytes(string33,'latin1')
        encoded43 = str(base64.b64encode(encoded42))
        encoded45 = 'Basic '+ encoded43

        encoded45 = encoded45[:-1]
        encoded45 = encoded45.replace("b'","")

        body1 = [('grant_type', 'authorization_code'),('code', code3)]

        headers = {'authorization': encoded45}

        r = requests.post('https://api.paypal.com/v1/identity/openidconnect/tokenservice', data = body1, headers = headers)

        resp = r.json()

        refreshtoken = resp['refresh_token']
        accesstoken = resp['access_token']


        return HttpResponse(r)


def paypalapigetaccess(request):
    if request.method=="GET":
        code21 = request.GET.get('pairing')

        if code21=="####":
            refreshtok="####"

            string33 = (code21 + ":" + '####')
            encoded42= bytes(string33,'latin1')
            encoded43 = str(base64.b64encode(encoded42))
            encoded45 = 'Basic '+ encoded43

            encoded45 = encoded45[:-1]
            encoded45 = encoded45.replace("b'","")
            headers = {
            'authorization': encoded45,
            'content-type': 'application/x-www-form-urlencoded',
            }

            data = [
              ('grant_type', 'refresh_token'),
              ('refresh_token', refreshtok),
            ]

            response = requests.post('https://api.paypal.com/v1/identity/openidconnect/tokenservice', headers=headers, data=data)

            resp = response.json()
            accesstok= resp['access_token']

            return HttpResponse(accesstok)
        else:
            return HttpResponse(None)



def privacypolicyuseragreement(request):
    if request.method =="GET":
        return HttpResponse("PRIVACY POLICY AND USER AGREEMENT This online service is hosted in Australia in secure, facilities. To help protect the privacy of data and personal information we collect and hold, we maintain physical, technical and administrative safeguards. We update and test our security technology on an ongoing basis. We train our employees about the importance of confidentiality and maintaining the privacy and security of your information. Access to your Personal Information is restricted to employees who need it to provide benefits or services to you.")




@api_view(['GET'])
@permission_classes((AllowAny,))
def salestoday(request):
    if request.method == "GET":
        resno = request.GET.get('resno')
        rescode = request.GET.get('id')
        if rescode =="####":

            startdate = request.GET.get('startdate')
            enddate = request.GET.get('enddate')
            sd=datetime.strptime(startdate,'%d-%m-%Y')
            ed= datetime.strptime(enddate,'%d-%m-%Y')
            now =sd.replace(hour=0, minute=0, second=0)
            now2 =ed.replace(hour=0, minute=0, second=0)
            dt = datetime.now().time()
            d1 = now - timedelta(hours=10)
            # ytd = now - timedelta(days=1)
            # d2 = now + timedelta(hours=14)
            ytd = now2
            d2 = now2 - timedelta(hours=10)

            now1=d2.date()
            ytd1= d1.date()
            d3 = d1.time()
            d4 = d2.time()
            # roq = request.META.get('HTTP_{ROQ}')
            # restaurant = Restaurants.objects.get(rescode=roq)
            # r = restaurant.resno



            details = Orders.objects.filter(resno= resno)
            details1 = details.filter(orderdate=ytd1, ordertime__gte=d3)
            details4 = details.filter(orderdate__gt=ytd1,orderdate__lt=now1)
            # details1 = details2.filter(ordertime__gte=d1)
            details3 = details.filter(orderdate=now1,ordertime__lte=d4)
            details2 = details1 | details3 | details4
            # details2 = details1.filter(ordertime__lte=d2)
            # details1 = details.filter(ordertime__gte=d1)
            list=[]
            total=0
            for row in details2:
                total += row.orderamount
                
            list = ({'total':str(total),"ytd":str(ytd1),"now":str(now1),"d1":str(d1),"d2":str(d2)})
            list_json = json.dumps(list)

            return HttpResponse(list_json, 'application/javascript')



        #         time=(row.ordertime).strftime('%H:%M:%S')
        #         orderamount = "{:.2f}".format(row.orderamount)
        #         orderss = OrderDetails.objects.filter(orderno=row.orderno)
        #         orderlist = []
        #         for a in orderss: 
        #             orderlist.append({'itemname':a.itemno.itemname,'quantity':int(a.quantity)})
                
        #         list.append({'ordertype':row.ordertype,'customerno':row.customerno.phone_number,'ordertime':time,'price':orderamount, 'orderrefno':row.orderrefno, 'pk':row.orderno, 'comments':row.comments,'items':orderlist})
        # # data = serializers.serialize('json', list(details1), fields=('ordertype', 'Customer__phone_number','orderamount', 'ordertime'))
        # list_json = json.dumps(list)
        # return HttpResponse(list_json, 'application/javascript')








@api_view(['POST'])
@permission_classes((AllowAny,))
def removeorder(request):
    if request.method == "POST":
        data=json.loads(request.body.decode('utf-8'))
        dd = data['orderrefno']
        ee = data['qq']
        if ee == "1533833":
            try:
                thisitem = Orders.objects.get(orderno=dd)

                thisitem.delete()
                return HttpResponse('Success')

                # orderdetails = Orderdetails.objects.filter(orderno=dd)
                # for a in orderdetails:
                #     a.delete()    
            except Menus.DoesNotExist:
                return HttpResponse('Error')
        else:
            return HttpResponse('error')




@api_view(['POST'])
@permission_classes((AllowAny,))
def confirmorder(request):
    if request.method == "POST":
        data=json.loads(request.body.decode('utf-8'))
        dd = data['orderrefno']
        ee = data['qq']
        if ee == "1533833":
            try:
                thisitem = Orders.objects.get(orderno=dd)

                thisitem.confirm = True
                thisitem.save()
                return HttpResponse("Success")

                # orderdetails = Orderdetails.objects.filter(orderno=dd)
                # for a in orderdetails:
                #     a.delete()    
            except Menus.DoesNotExist:
                return HttpResponse('Error')
        else:
            return HttpResponse('error')











@api_view(['POST'])
@permission_classes((AllowAny,))
def pingentry(request):
    if request.method == "POST":
        data=json.loads(request.body.decode('utf-8'))
        dd = data['orderrefno']
        ee = data['qq']
        if ee == "1533833":

            res = Restaurants.objects.get(resno=dd)        
            sockid= res.rescode
         
            a1234 = Orders.objects.filter(resno=dd, confirm=False)
            for order in a1234:
                orderrefno = order.orderrefno
                orderno = order.orderno
                comments = order.comments
                customerno = order.customerno.phone_number
                time1=order.ordertime.strftime('%H:%M:%S')
                orderamount = "{:.2f}".format(order.orderamount)
                ordertype = order.ordertype


                values={'name':orderno, 'socketid': sockid, 'customerno':customerno, 'price':orderamount, 'orderno':orderrefno, 'time':time1 , 'ordertype':ordertype, 'comments':comments}
                headers =  {'content-type': 'application/json'}
                r=requests.post('http://####:3001/', data=json.dumps(values), headers=headers) 
            
            return HttpResponse(res.connected)
                # orderdetails = Orderdetails.objects.filter(orderno=dd)
                # for a in orderdetails:
                #     a.delete()    
            # except Menus.DoesNotExist:
            #     return HttpResponse('Error')
        else:
            return HttpResponse('error')






# @api_view(['POST'])
@permission_classes((AllowAny,))
def querycheck213(request):
    if request.method == "GET":
        # data=json.loads(request.body.decode('utf-8'))
        # dd = data['orderrefno']
        # ee = data['qq']
        # if ee == "1533833":
        # res = Restaurants.objects.get(resno=dd)        
        # sockid= res.rescode
     
        a1234 = Orders.objects.filter(confirm=False)
        return HttpResponse(a1234)
        # for order in a1234:
        #     orderrefno = order.orderrefno
        #     orderno = order.orderno
        #     comments = order.comments
        #     customerno = order.customerno.phone_number
        #     time1=order.ordertime.strftime('%H:%M:%S')
        #     orderamount = "{:.2f}".format(order.orderamount)
        #     ordertype = order.ordertype


            # values={'name':orderno, 'socketid': sockid, 'customerno':customerno, 'price':orderamount, 'orderno':orderrefno, 'time':time1 , 'ordertype':ordertype, 'comments':comments}
            # headers =  {'content-type': 'application/json'}
            # r=requests.post('http://####:3001/', data=json.dumps(values), headers=headers) 
        
        # return HttpResponse('success')
            # orderdetails = Orderdetails.objects.filter(orderno=dd)
            # for a in orderdetails:
            #     a.delete()    
        # except Menus.DoesNotExist:
        #     return HttpResponse('Error')
    else:
        return HttpResponse('error')











@permission_classes((AllowAny,))
def querycheck2133(request):
    if request.method == "GET":

        resno1 = request.GET.get('resno')

        Rest = Restaurants.objects.get(resno=resno1)
     
        a1234 = Orders.objects.filter(resno=Rest)





        allbookings = a1234
        paginator = Paginator(allbookings, 70)    
        page = request.GET.get('page')
        try:
            allbookings = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            allbookings = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            allbookings = paginator.page(paginator.num_pages)

        # if request.GET.get('page'):
        #     # resp = serialize_debates(page_objects)
        #     return JsonResponse({
        #     'allbookings': allbookings
        # })


    context = {
    'allbookings':allbookings,

    }
    return render(request,"eatapp/allbooking.html",context)

