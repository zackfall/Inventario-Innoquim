# Generated manually for RecepcionMaterial model update

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('materia_prima', '0001_initial'),
        ('recepcion_material', '0001_initial'),
    ]

    operations = [
        # Renombrar campo id_almacen a almacen
        migrations.RenameField(
            model_name='recepcionmaterial',
            old_name='id_almacen',
            new_name='almacen',
        ),
        
        # Agregar nuevos campos como nulables primero
        migrations.AddField(
            model_name='recepcionmaterial',
            name='materia_prima',
            field=models.ForeignKey(blank=True, help_text='Materia prima principal de esta recepción', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recepciones_principales', to='materia_prima.materiaprima'),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='cantidad',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Cantidad total recibida', max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='costo_unitario',
            field=models.DecimalField(blank=True, decimal_places=4, help_text='Costo unitario por unidad de materia prima', max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total de la recepción (cantidad × costo_unitario)', max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='proveedor',
            field=models.CharField(blank=True, help_text='Nombre del proveedor', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='fecha_de_recepcion',
            field=models.DateField(blank=True, help_text='Fecha en que se recibió el material', null=True),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='numero_de_factura',
            field=models.CharField(blank=True, help_text='Número de factura del proveedor', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='recepcionmaterial',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Eliminar campo antiguo fecha_recepcion (auto_now_add)
        migrations.RemoveField(
            model_name='recepcionmaterial',
            name='fecha_recepcion',
        ),
        
        # Agregar campo fecha_creacion con auto_now_add
        migrations.AddField(
            model_name='recepcionmaterial',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
