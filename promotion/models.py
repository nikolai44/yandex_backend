from django.db import models

# Create your models here.


class Gender(models.TextChoices):
    male = 'Male'
    female = 'Female'


class Citizen(models.Model):
    citizen_id = models.PositiveIntegerField()
    town = models.CharField(max_length=256, null=False)
    street = models.CharField(max_length=256)
    building = models.CharField(max_length=256)
    apartment = models.PositiveIntegerField()
    name = models.CharField(max_length=256)
    birth_date = models.DateField()
    gender = models.CharField(choices=Gender.choices, max_length=6)
    import_group = models.ForeignKey("Import", related_name="citizens", on_delete=models.CASCADE, blank=True)
    relatives = models.ManyToManyField("self")

    def add_relatives(self, import_table, relatives):
        for relative in relatives:
            r = list(import_table.citizens.filter(citizen_id=relative))
            self.relatives.add(*r)

    def add_relatives_by_import_id(self, import_id, relatives_ids):
        import_table = Import.get_import_obj_by_import_id(import_id)
        for relative in relatives_ids:
            r = list(import_table.citizens.filter(citizen_id=relative))
            self.relatives.add(*r)
        for relative in self.relatives.all():
            if relative.citizen_id not in relatives_ids:
                self.relatives.remove(relative)

    def get_relatives(self):
        return self.relatives.all()

    @staticmethod
    def get_citizen_by_import_id_citizen_id(import_id, citizen_id):
        i = Import.get_import_obj_by_import_id(import_id)
        return i.citizens.filter(citizen_id=citizen_id)[0]


class Import(models.Model):
    import_id = models.AutoField(primary_key=True)

    @staticmethod
    def get_import_obj_by_import_id(import_id):
        return Import.objects.filter(import_id=import_id)[0]

    @staticmethod
    def get_citizens_by_import_id(import_id):
        return Import.objects.filter(import_id=import_id)[0].citizens.all()
