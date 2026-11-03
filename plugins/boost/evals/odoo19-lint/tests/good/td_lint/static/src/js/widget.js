/** @odoo-module **/
import { Component } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";

// раньше было useService("rpc") — в 19.0 так нельзя
export class TicketWidget extends Component {
    setup() {
        this.rpc = rpc;
        this.user = user;
        this.orm = useService("orm");
    }
}
