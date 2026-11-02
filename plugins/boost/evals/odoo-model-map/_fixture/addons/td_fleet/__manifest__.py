{
    "name": "TD Fleet",
    "version": "19.0.1.0.0",
    "category": "Operations",
    "summary": "Vehicles and drivers",
    "depends": ["base", "mail"],
    "data": [
        "security/td_fleet_security.xml",
        "security/ir.model.access.csv",
        "data/td_vehicle_tag_data.xml",
        "views/td_vehicle_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
