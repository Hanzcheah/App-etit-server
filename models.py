from django.db import models
from django.contrib.gis.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Customer(models.Model):
    customerno = models.CharField(max_length=100, null=True, blank=True, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    totalspent = models.DecimalField(max_digits=7, decimal_places=2)
    password = models.CharField(max_length=15)


    def __str__ (self):
       return self.name

def upload_location(instance, filename):
  return "%s/%s" %(instance.name, filename)

class Restaurants(models.Model):
    resno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    resdescription = models.TextField()
    last_modified_date = models.DateField()
    rescode = models.CharField(max_length=100)
    respassword = models.CharField(max_length=100)
    image = models.ImageField(upload_to=upload_location, blank=True, null=True)
    location = models.PointField(blank=True, null=True)
    connected = models.BooleanField(default=False)
    exid = models.CharField(max_length=100, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number format: +60412345678.")
    phone_number = models.CharField(validators=[phone_regex], max_length=16 )
    tablenumber= models.BooleanField(default=False)
    dinein = models.BooleanField(default=False)
    takeaway = models.BooleanField(default=False)
    codedmsg = models.CharField(max_length=100, blank=True, null=True)
    def __str__ (self):
       return self.name 






class Categories(models.Model):
    categoriesno = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100) 
    catimage = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    resno = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    rankno = models.IntegerField(blank=True, null=True)

    def __str__ (self):
       return self.category 

def upload_location(instance, filename):
  return "%s/%s" %(instance.itemno, filename)

class Menus(models.Model):
   itemno = models.AutoField(primary_key=True)
   itemname = models.CharField(max_length=100)
   itemothername = models.CharField(max_length=100,blank=True, null=True)
   resno = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
   itemdescription = models.TextField(null=True)
   itemimage = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
   itemprice = models.DecimalField(max_digits=6, decimal_places=2)
   categoriesno = models.ForeignKey(Categories, on_delete=models.CASCADE)
   hidden = models.BooleanField(default=False)
   printerno = models.CharField(max_length=4,blank=True, null=True)
   extraitem = models.BooleanField(default=False)

   def __str__ (self):
       return self.itemname 



class Orders(models.Model):
    orderno = models.CharField(max_length=100, primary_key=True)
    orderdate = models.DateField()
    ordertime = models.TimeField(auto_now_add=True, null=True, blank=True)
    customerno = models.ForeignKey(Customer, to_field="customerno", db_column="customerno")
    orderamount = models.DecimalField(max_digits=6, decimal_places=2)
    resno = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    orderscompleted = models.BooleanField(default=False)  
    ordertype = models.CharField(max_length=40, blank=True, null=True)
    orderrefno = models.CharField(max_length=4, blank = True, null=True)
    comments = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=40,default="Cooking")
    gst = models.DecimalField(max_digits=6, decimal_places=2,null=True, blank=True)
    confirm = models.BooleanField(default=False)

    def __str__ (self):
       return self.orderno 

class OrderDetails(models.Model):
    orderdetailsno = models.AutoField(primary_key=True)
    orderno = models.ForeignKey(Orders, on_delete=models.CASCADE)
    itemno = models.ForeignKey(Menus)
    quantity = models.DecimalField(max_digits=50, decimal_places=2)
    resno = models.ForeignKey(Restaurants,on_delete= models.CASCADE)
    status = models.CharField(max_length=40,default="Cooking")

    def __str__ (self):
       return self.orderdetailsno 




class Tablenum(models.Model):
    tableno = models.AutoField(primary_key=True)
    tablenum = models.CharField(max_length=100)
    resno = models.ForeignKey(Restaurants, on_delete=models.CASCADE)

    def __str__ (self):
       return self.tablenum 




class Extraitems(models.Model):
   itemno = models.AutoField(primary_key=True)
   itemname = models.CharField(max_length=100)
   resno = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
   itemdescription = models.TextField(null=True)
   itemimage = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
   itemprice = models.DecimalField(max_digits=6, decimal_places=2)
   itemno = models.ForeignKey(Menus, on_delete=models.CASCADE)
   hidden = models.BooleanField(default=False)


   def __str__ (self):
       return self.itemname 
