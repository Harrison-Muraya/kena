from django.db import migrations, models
import hashlib
import json

def create_genesis_block(apps, schema_editor):
    Block = apps.get_model('coin', 'Block')
    if not Block.objects.exists():
        genesis_data = {
            "height": 0,
            "nonce": 0,
            "timestamp": 0,
            "previous_hash": "0" * 64,
            "transactions": []
        }
        hash_string = json.dumps(genesis_data, sort_keys=True).encode()
        genesis_hash = hashlib.sha256(hash_string).hexdigest()

    Block.objects.create(
        height=genesis_data["height"],
        nonce=genesis_data["nonce"],
        timestamp=genesis_data["timestamp"],
        previous_hash=genesis_data["previous_hash"],
        hash=genesis_hash,
        transactions=genesis_data["transactions"]
    )

class Migration(migrations.Migration):

    dependencies = [
        ('coin', '0006_auto_20250805_1404'),
    ]

    operations = [
        migrations.RunPython(create_genesis_block),
    ]
