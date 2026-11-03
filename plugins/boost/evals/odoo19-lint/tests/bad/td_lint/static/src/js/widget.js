/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TicketWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.user = useService("user");
        this.orm = useService("orm");
    }
}
