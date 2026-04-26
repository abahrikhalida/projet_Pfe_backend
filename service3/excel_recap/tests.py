# # tests/test_models.py
# from django.test import TestCase
# from django.core.exceptions import ValidationError
# from excel_recap.models import BudgetRecord

# class BudgetRecordValidationTest(TestCase):
    
#     def test_total_less_than_dex_raises_error(self):
#         record = BudgetRecord(
#             cout_initial_total=100,
#             cout_initial_dont_dex=150  # DEX > Total
#         )
        
#         with self.assertRaises(ValidationError):
#             record.clean()
    
#     def test_total_equal_to_dex_is_valid(self):
#         record = BudgetRecord(
#             cout_initial_total=100,
#             cout_initial_dont_dex=100  # DEX = Total
#         )
        
#         try:
#             record.clean()  # Ne doit pas lever d'erreur
#         except ValidationError:
#             self.fail("ValidationError raised when total == dex")
    
#     def test_total_greater_than_dex_is_valid(self):
#         record = BudgetRecord(
#             cout_initial_total=150,
#             cout_initial_dont_dex=100  # DEX < Total
#         )
        
#         try:
#             record.clean()
#         except ValidationError:
#             self.fail("ValidationError raised when total > dex")
# Dans votre tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import BudgetRecord

class BudgetRecordValidationTest(TestCase):
    
    def test_validation_passes_when_total_greater_than_dex(self):
        """Test que la validation réussit quand total > dex"""
        record = BudgetRecord(
            cout_initial_total=500,
            cout_initial_dont_dex=300
        )
        
        try:
            record.clean()
            print("✅ SUCCÈS: La validation a accepté total > dex")
        except ValidationError:
            self.fail("❌ ÉCHEC: La validation a rejeté alors que total > dex")
    
    def test_validation_passes_when_total_equal_dex(self):
        """Test que la validation réussit quand total = dex"""
        record = BudgetRecord(
            cout_initial_total=500,
            cout_initial_dont_dex=800
        )
        
        try:
            record.clean()
            print("✅ SUCCÈS: La validation a accepté total = dex")
        except ValidationError:
            self.fail("❌ ÉCHEC: La validation a rejeté alors que total = dex")
    
    def test_validation_fails_when_total_less_than_dex(self):
        """Test que la validation échoue quand total < dex"""
        record = BudgetRecord(
            cout_initial_total=300,
            cout_initial_dont_dex=500
        )
        
        with self.assertRaises(ValidationError):
            record.clean()
            print("✅ SUCCÈS: La validation a bien rejeté total < dex")