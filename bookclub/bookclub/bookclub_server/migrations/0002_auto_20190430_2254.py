# Generated by Django 2.1.7 on 2019-04-30 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub_server', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suggestion',
            old_name='suggestionDate',
            new_name='suggestion_date',
        ),
        migrations.RemoveField(
            model_name='suggestion',
            name='book_id',
        ),
        migrations.RemoveField(
            model_name='suggestion',
            name='suggestionInformation',
        ),
        migrations.AddField(
            model_name='chat',
            name='match_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookclub_server.Match'),
        ),
        migrations.AddField(
            model_name='chat',
            name='suggestion_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookclub_server.Suggestion'),
        ),
        migrations.AddField(
            model_name='history',
            name='suggestion_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='suggestion_id', to='bookclub_server.Suggestion'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='giving_book',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='giving_book_suggestion', to='bookclub_server.Book'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='state',
            field=models.CharField(default='nothing', max_length=250),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='suggested_book_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='suggested_book', to='bookclub_server.Book'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='suggested_user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='suggested_user', to='bookclub_server.User'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='wanted_book',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='wanted_book_suggestion', to='bookclub_server.Book'),
        ),
        migrations.AlterField(
            model_name='history',
            name='match_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='match_id', to='bookclub_server.Match'),
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='user_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_id_suggestion', to='bookclub_server.User'),
        ),
    ]