from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db import models
from datetime import datetime

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, area=None, **extra_fields):
        if not area:
            print("# Crear un área por defecto si no se proporciona una")
            area, created = Area.objects.get_or_create(name="Default Area", code="DEFAULT", is_deposit = False)

        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, area=area, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, area=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, area, **extra_fields)

    
class SystemConfigKeyValues(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

def get_system_config_value(key, default=None):
    try:
        return SystemConfigKeyValues.objects.get(key=key).value
    except SystemConfigKeyValues.DoesNotExist:
        return default

def get_default_archive():
    return get_system_config_value('default_archive_code')

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('manager', 'Manager'),
        ('archive_responsible', 'Archive Responsible'),
        ('admin', 'System Administrator')
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    area = models.ForeignKey('Area', on_delete=models.PROTECT, verbose_name="User Area")
    deposit = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        default=get_default_archive,
        verbose_name="Archive",
        related_name='deposits'
    )
    objects = UserManager() 
    USERNAME_FIELD = 'username'  
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']  

    

class Area(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Area Code")
    name = models.CharField(max_length=100, unique=True, verbose_name="Area Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_deposit = models.BooleanField(default=False, verbose_name="Is Deposit")

    def __str__(self):
        return self.name
    
 
class BoxType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Box Type")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return self.name

class Box(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('waiting_close', 'Waiting for Close'),
        ('waiting_archive', 'Waiting for Archive'),
        ('accepted_archive', 'Accepted by Archive Responsible'),
        ('archived', 'In Archive'),

 
    
    ]
    name = models.CharField(max_length = 10, primary_key=False, verbose_name="Box Name", null=False, blank=False, unique=True)  
    box_type = models.ForeignKey(BoxType, on_delete=models.PROTECT, related_name="boxes")
    description = models.TextField(blank=True, null=True, verbose_name="Box Description")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="boxes")
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="boxes")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='open')
    id = models.AutoField(primary_key=True, verbose_name="Box ID")  # Auto-incremental ID
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    update_date =  models.DateTimeField(auto_now=True)
    close_date = models.DateTimeField(blank=True, null=True, default=None, verbose_name="Close Date")
    current_year = datetime.now().year

    destruction_year = models.PositiveSmallIntegerField(
        choices=[(0,'Never')] + [(year, str(year)) for year in range(current_year, current_year + 500)],
        verbose_name="Destruction Year"
    )
    current_area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="current_boxes", verbose_name="Current Area")
    total_sheets = models.PositiveIntegerField(default=0)  
   
    def update_total_sheets(self):
        """
        Recalculate the total number of sheets from associated documents.
        """
        self.total_sheets = self.documentations.aggregate(
            total=models.Sum('sheets')
        )['total'] or 0
        self.update_date = datetime.now()
        self.save()
    
    
    def close_box(self):
        """Close the box and set the close_date to the current time."""
        self.status = 'closed'
        self.close_date = models.DateTimeField(auto_now_add=True)
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.name:
            # Obtener el último número utilizado
            last_box = Box.objects.order_by('-id').first()
            if last_box and last_box.name.isdigit():
                new_number = int(last_box.name) + 1
            else:
                new_number = 1

            self.name = f"{new_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Box ({self.box_type.name}) - {self.status}"




class DocType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Document Type")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return self.name


class Documentation(models.Model):
    cuit_number = models.PositiveIntegerField(null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)  # Required
    doc_type = models.ForeignKey(DocType, on_delete=models.PROTECT, related_name="documents")
    description = models.TextField(blank=True, null=True, verbose_name="Document Description")
    corpus = models.TextField(null=False, blank=False)  # Required
    sheets = models.PositiveIntegerField(null=False, blank=False)  # Required
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)  # Creators
    creation_date = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    box = models.ForeignKey(Box, on_delete=models.SET_NULL, null= True, blank = True, related_name="documentations")  # Relation to Box

    def __str__(self):
        return f"{self.name} (Box: {self.box.name})"


    



class Universe(models.Model):
    doc_number = models.PositiveIntegerField(null=False, blank=False)  
    name = models.TextField(max_length=255, blank=True, null=False)  

    def __str__(self):
        return f"{self.doc_number}: {self.name}"



class BoxLog(models.Model):
    LOG_TYPE_CHOICES = [
        ('new', 'New Box'),
        ('change_area', 'Change of Area'),
        ('doc_added', 'Document Added'),
        ('doc_removed', 'Document Removed'),
        ('doc_edited', 'Document Edited'),
        ('status_change', "Status Changed"),
        ('area_change', 'Area Changed'),
    ]
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    box = models.ForeignKey("Box", on_delete=models.PROTECT, related_name="logs")
    area_origin = models.ForeignKey("Area", on_delete=models.PROTECT, null=True, blank=True, related_name="origin_logs")
    area_destination = models.ForeignKey("Area", on_delete=models.PROTECT, null=True, blank=True, related_name="destination_logs")
    doc_added = models.ForeignKey("Documentation", on_delete=models.SET_NULL, null=True, blank=True, related_name="logs_added")  
    doc_removed = models.ForeignKey("Documentation", on_delete=models.SET_NULL, null=True, blank=True, related_name="logs_removed")  
    previous_status = models.CharField(max_length=50, null=False, blank=False)
    new_status = models.CharField(max_length=50, null=False, blank=False)
    observations = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    user_area = models.ForeignKey("Area", on_delete=models.PROTECT, related_name="user_logs")
    log_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for Box {self.box.id} - {self.previous_status} to {self.new_status}"

