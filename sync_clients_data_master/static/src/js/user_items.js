/** @odoo-module **/

import {registry} from "@web/core/registry";
import {browser} from "@web/core/browser/browser";
import {UserMenu} from "@web/webclient/user_menu/user_menu";

registry.category("user_menuitems").remove("odoo_account");

function viewDemo(env) {
    return {
        type: "item",
        id: "view_demo",
        description: env._t("View Demo"),
        callback: () => {
            window.open("http://139.59.57.58:8074/web/login");
        },
        sequence: 70,
    };
}
registry.category("user_menuitems").add("view_demo", viewDemo, {force: true});
