from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('almacen', '0001_initial'),
        ('unidad', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventarioMaterial',
            fields=[
                ('inventario_material_id', models.CharField(editable=False, help_text='Codigo unico autogenerado (formato: IM000001)', max_length=8, primary_key=True, serialize=False, verbose_name='ID Inventario Material')),
                ('object_id', models.CharField(help_text='ID externo del ítem (MPnnnnnn o product_code)', max_length=50, verbose_name='Identificador del Ítem')),
                ('cantidad', models.DecimalField(decimal_places=2, default=0, help_text='Cantidad actual en stock', max_digits=10, verbose_name='Cantidad Disponible')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Ultima Actualizacion')),
                ('almacen_id', models.ForeignKey(help_text='Ubicacion fisica donde esta el material', on_delete=django.db.models.deletion.PROTECT, to='almacen.almacen', verbose_name='Almacen')),
                ('content_type', models.ForeignKey(help_text='Modelo del ítem inventariado (MateriaPrima o Producto)', on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype', verbose_name='Tipo de Ítem')),
                ('unidad_id', models.ForeignKey(help_text='Unidad en que se mide la cantidad (kg, litros, etc)', on_delete=django.db.models.deletion.PROTECT, to='unidad.unidad', verbose_name='Unidad de Medida')),
            ],
            options={
                'verbose_name': 'Inventario de Ítems',
                'verbose_name_plural': 'Inventarios de Ítems',
                'db_table': 'inventario_material',
                'ordering': ['inventario_material_id'],
                'unique_together': {('content_type', 'object_id', 'almacen_id')},
            },
        ),
        migrations.AddIndex(
            model_name='inventariomaterial',
            index=models.Index(fields=['content_type', 'object_id'], name='inventario_content_object_idx'),
        ),
        migrations.AddIndex(
            model_name='inventariomaterial',
            index=models.Index(fields=['almacen_id'], name='inventario_almacen_idx'),
        ),
    ]
