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
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/fetch_client_data.xml",
        "data/invoice_product_data.xml",
        "views/client_data_view.xml",
        "views/res_partner_view.xml",
        "views/account_move_views.xml",
    ],
    "assets": {
        "web.assets_common": [
            "sync_clients_data_master/static/src/js/user_items.js",
        ]
    },
    "application": True,
    "installable": True,
}
