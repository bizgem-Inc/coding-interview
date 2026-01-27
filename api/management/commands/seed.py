from django.core.management.base import BaseCommand
from api.models.company import Company
from api.models.category import Category


class Command(BaseCommand):
    help = 'テストデータをデータベースに投入します'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding開始...'))

        # 既存データの削除
        Category.objects.all().delete()
        Company.objects.all().delete()
        
        # 企業データの作成
        companies = []
        company_data = [
            {"name": "株式会社テストカンパニーA"},
            {"name": "株式会社テストカンパニーB"},
            {"name": "株式会社テストカンパニーC"},
        ]
        
        for data in company_data:
            company = Company.objects.create(**data)
            companies.append(company)
            self.stdout.write(self.style.SUCCESS(f'企業作成: {company.name} (ID: {company.id})'))

        # カテゴリデータの作成
        # 企業Aのカテゴリ
        company_a = companies[0]
        
        # 親カテゴリ
        category_a1 = Category.objects.create(
            company=company_a,
            name="電化製品",
            parent_category=None
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_a1.name} (ID: {category_a1.id})'))
        
        category_a2 = Category.objects.create(
            company=company_a,
            name="家具",
            parent_category=None
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_a2.name} (ID: {category_a2.id})'))
        
        # 子カテゴリ（電化製品の下）
        category_a1_1 = Category.objects.create(
            company=company_a,
            name="テレビ",
            parent_category=category_a1
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_a1_1.name} (親: {category_a1.name}, ID: {category_a1_1.id})'))
        
        category_a1_2 = Category.objects.create(
            company=company_a,
            name="冷蔵庫",
            parent_category=category_a1
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_a1_2.name} (親: {category_a1.name}, ID: {category_a1_2.id})'))
        
        # 子カテゴリ（家具の下）
        category_a2_1 = Category.objects.create(
            company=company_a,
            name="ソファ",
            parent_category=category_a2
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_a2_1.name} (親: {category_a2.name}, ID: {category_a2_1.id})'))

        # 企業Bのカテゴリ
        company_b = companies[1]
        
        category_b1 = Category.objects.create(
            company=company_b,
            name="食品",
            parent_category=None
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_b1.name} (ID: {category_b1.id})'))
        
        category_b1_1 = Category.objects.create(
            company=company_b,
            name="野菜",
            parent_category=category_b1
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_b1_1.name} (親: {category_b1.name}, ID: {category_b1_1.id})'))
        
        category_b1_2 = Category.objects.create(
            company=company_b,
            name="果物",
            parent_category=category_b1
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_b1_2.name} (親: {category_b1.name}, ID: {category_b1_2.id})'))

        # 企業Cのカテゴリ
        company_c = companies[2]
        
        category_c1 = Category.objects.create(
            company=company_c,
            name="書籍",
            parent_category=None
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_c1.name} (ID: {category_c1.id})'))
        
        category_c2 = Category.objects.create(
            company=company_c,
            name="文房具",
            parent_category=None
        )
        self.stdout.write(self.style.SUCCESS(f'カテゴリ作成: {category_c2.name} (ID: {category_c2.id})'))

        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Seeding完了！'))
        self.stdout.write(self.style.SUCCESS(f'企業数: {Company.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'カテゴリ数: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
