from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWorkshopOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer", "phone": "+380 44 123-45-67"})

    def test_sequence_assigned(self):
        order = self.env["td.workshop.order"].create(
            {"partner_id": self.partner.id, "device": "Laptop"}
        )
        self.assertNotEqual(order.name, "New")

    def test_phone_copied(self):
        order = self.env["td.workshop.order"].create(
            {"partner_id": self.partner.id, "device": "Phone"}
        )
        self.assertEqual(order.customer_phone, "+380441234567")
