{
    "name": "TD Fleet Service",
    "version": "19.0.1.0.0",
    "category": "Operations",
    "summary": "Service log and service cards for vehicles",
    "depends": ["td_fleet"],
    "data": [
        "security/td_fleet_service_security.xml",
        "security/ir.model.access.csv",
        "views/td_vehicle_service_views.xml",
        "views/td_vehicle_views.xml",
        "data/td_vehicle_service_actions.xml",
    ],
    "license": "LGPL-3",
}
