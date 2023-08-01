# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Spequa Billing Portal",
    "version": "16.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "license": "AGPL-3",
    "website": "http://www.serpentcs.com",
    "category": "Tools",
    "depends": [
        "mail",
        "base_vat",
        "l10n_in",
        "stock",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/customers_minimum_balance_list_email_template.xml",
        "data/fetch_client_data.xml",
        "data/minimum_balance_data.xml",
        "data/invoice_product_data.xml",
        "views/client_data_view.xml",
        "views/res_partner_view.xml",
        "views/account_move_views.xml",
        "views/balance_history_views.xml",
        "views/spequa_charges_views.xml",
        "views/product_template_views.xml",
    ],
    "assets": {
        "web.assets_common": [
            "sync_clients_data_master/static/src/js/user_items.js",
        ]
    },
    "application": True,
    "installable": True,
}
