from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date
from inventory.models import Product, InventoryLog, Staff


class Command(BaseCommand):
    help = 'Automatically write off expired products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of staff member performing the write-off (defaults to "system")',
            default='system'
        )

    def handle(self, *args, **options):
        username = options['username']
        today = date.today()
        
        # Get or create system staff member
        try:
            staff = Staff.objects.get(username=username)
        except Staff.DoesNotExist:
            if username == 'system':
                # Create system staff if it doesn't exist
                staff = Staff.objects.create(
                    first_name='System',
                    last_name='User',
                    role='Admin',
                    username='system',
                    password_hash='system_user'
                )
                self.stdout.write(
                    self.style.WARNING(f'Created system user: {staff.username}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Staff member with username "{username}" not found')
                )
                return

        # Query expired products with stock
        expired_products = Product.objects.filter(
            expiry_date__lt=today,
            stock_quantity__gt=0
        )

        if not expired_products.exists():
            self.stdout.write(
                self.style.SUCCESS('No expired products found to write off')
            )
            return

        self.stdout.write(
            f'Found {expired_products.count()} expired products to write off'
        )

        # Process write-offs in a transaction
        with transaction.atomic():
            total_loss = 0
            processed_count = 0
            
            for product in expired_products:
                qty_before = product.stock_quantity

                # Create inventory log entry
                InventoryLog.objects.create(
                    staff=staff,
                    product=product,
                    log_type='Adjustment',
                    quantity=-qty_before,
                    remarks='expiry_writeoff',
                    log_date=timezone.now()
                )
                
                # Calculate loss
                loss_amount = qty_before * product.unit_cost
                total_loss += loss_amount
                
                # Set stock quantity to 0
                product.stock_quantity = 0
                product.save()
                
                processed_count += 1
                
                self.stdout.write(
                    f'Write-off: {product.product_name} - '
                    f'{qty_before} units (${loss_amount:.2f})'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully wrote off {processed_count} expired products. '
                f'Total loss: ${total_loss:.2f}'
            )
        )
