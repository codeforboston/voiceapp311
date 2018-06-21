import os

# CSV files for testing location_util's csv functions
PARKING_LOTS_TEST_CSV = os.path.join(
    os.getcwd(),
    "mycity/test/test_data/Snow_Emergency_Parking.csv"
)

# because getcwd() will be run from project root,
# we need to append test_data's path
PARKING_LOTS_TEST_DATA = os.path.join(
    os.getcwd(),
    "mycity/test/test_data/parking_lots"
)
PARKING_LOTS_ADDR_INDEX = 7


##################################################################
# Mocked returns for patched functions that access web resources #
##################################################################


# Alexa device address
ALEXA_DEVICE_ADDRESS = {
    "addressLine1": "866 Huntington ave",
    "addressLine2": "null",
    "addressLine3": "null",
    "districtOrCounty": "null",
    "stateOrRegion": "Ma",
    "city": "Boston",
    "countryCode": "US",
    "postalCode": "02138"
}

# gis_utils.get_closest_feature
GOOGLE_MAPS_JSON = [
    {
        'Driving distance': 2458,
        'Driving distance text': '1.5 mi',
        'Driving time': 427,
        'Driving time text': '7 mins',
        'test': '94 Sawyer Ave Boston, MA'
    },
    {
        'Driving distance': 692625,
        'Driving distance text': '430 mi',
        'Driving time': 24533,
        'Driving time text': '6 hours 49 mins',
        'test': '4 Olivewood Ct Greenbelt, MD'
    }
]


# gis_utils._get_dest_addresses_from_features
PARKING_LOT_FEATURES = [
    [
        1,
        1,
        60,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #003',
        '115 Harvard Ave',
        ' ',
        0,
        ' ',
        '1bc385c4-285f-49d6-a606-151380906d38',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS',
        {
            'x': -7918414.198468381,
            'y': 5213945.511252668
        }
    ],
    [
        2,
        2,
        42,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #002',
        '398 Market St',
        ' ',
        0,
        ' ',
        'a9fcf634-ae60-407a-8b05-9bcac6bfeb63',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS',
        {
            'x': -7920695.3886001585,
            'y': 5213501.824205618
        }
    ],
    [
        4,
        4,
        18,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #034',
        '1891 Centre Street',
        ' ',
        0,
        ' ',
        '0cddfbc4-5afb-40fb-a783-d9f98c95f3a7',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS',
        {
            'x': -7921074.252411649,
            'y': 5203874.208464791
        }
    ]
]

# Trash Day intent
GET_ADDRESS_API_MOCK = {
    'parcel_id': 31460684,
    'area_id': 311,
    'service_id': 310,
    'area_name': 'Boston', # makes sense
    'place_id': 0,
    'name': '1000 Dorchester Ave, Boston, 02125'
}

GET_TRASH_DAY_MOCK = {
    'place': {
        'house': '1000',
        'unit': '',
        'lng': '36.6748',
        'country': 'usa',
        'id': 'D016B622-5C5A-11E7-A191-7A9C724EA4D6',
        'lat': '-40.28489',
        'name': '1000 Dorchester Ave, Boston, 02125',
        'locale': 'en-US',
        'source': 'recollect',
        'city': 'boston',
        'province': 'massachusetts',
        'street': 'dorchester ave'
    },
    'next_event': {
        'custom_subject': '',
        'id': 2045085,
        'is_approved': 1,
        'zone_id': 5255,
        'flags': [
            {
                'is_week_long': 0,
                'service_name': 'waste',
                'event_type': 'pickup',
                'plain_text_message': None,
                'icon': 'garbage_bag2:rgb(64,64,64)',
                'sort_order': 2,
                'subject': 'Trash',
                'opts': {
                    'event_type': 'pickup',
                    'event_proto': {'calendar_only': 0}
                },
                'borderColor': '#404040',
                'short_text_message': None,
                'voice_message': None,
                'html_message': 'Bags or barrels must be no larger than 32 gallons in capacity.',
                'icon_uri_fragment': '64,64,64/garbage_bag2',
                'color': '#404040',
                'name': 'Trash',
                'backgroundColor': '#404040',
                'area_name': 'Boston', 'id': 459
            },
            {
                'icon_uri_fragment': '0,89,222/recycle',
                'color': '#0059de',
                'short_text_message': None,
                'voice_message': None,
                'html_message': '<a target="_blank" href="http://rco.io/HML77">Acceptable papers and containers</a> are collected for recycling.',
                'id': 457,
                'name': 'Recycling',
                'backgroundColor': '#0059de',
                'area_name': 'Boston',
                'subject': 'Recycling',
                'borderColor': '#0059de',
                'opts': {
                    'event_proto': {'calendar_only': 0},
                    'event_type': 'pickup'
                },
                'plain_text_message': None,
                'sort_order': 3,
                'icon': 'recycle:rgb(0,89,222)',
                'is_week_long': 0,
                'service_name': 'waste',
                'event_type': 'pickup'
            }
        ],
        'options': {},
        'opts': {'calendar_only': 0},
        'zone': {
            'line_colour': 'FFFFFF',
            'pdf_uri': {},
            'name': 'boston-recollect-f',
            'id': 5255,
            'loc_title': {'en': 'Friday'},
            'show_when_empty': 0,
            'has_unapproved_future_events': 0,
            'is_empty': 0,
            'has_geom': 0,
            'opts': {},
            'has_parcels': 1,
            'priority': 0,
            'title': 'Friday',
            'description': {},
            'link_uri': {},
            'service_id': 310,
            'link_text': {},
            'colour_name': 'boston-recollect-f',
            'poly_colour': 'FFFFFF'
        },
        'custom_message': '',
        'day': '2018-05-04'
    },
    'service': {
        'name': 'waste',
        'signup_url': {
            'en': 'http://www.cityofboston.gov/publicworks/wastereduction/holiday.asp',
            'en-US': 'https://www.boston.gov/trash-day-schedule'
        },
        'id': 310,
        'pdf_style': {
            'Default': {
                'alert-info-bg': '#d9eef7',
                'btn-success-border': '#67BB4D',
                'navbar-default-border': '#67BB4D',
                'text-color': '#333333',
                'btn-success-bg': '#59A343',
                'btn-success-color': '#FFFFFF',
                'btn-default-border': '#cccccc',
                'btn-default-bg': '#FFFFFF',
                'link-hover-color': '#86c655',
                'link-color': '#508527',
                'btn-danger-border': '#bd362f',
                'btn-danger-color': '#FFFFFF',
                'alert-info-border': '#bce8f1',
                'widget-border': '#ececec',
                'calendar-border': '#dddddd',
                'navbar-default-bg': '#59A343',
                'btn-default-color': '#333333',
                'btn-danger-bg': '#ee5f5b',
                'alert-info-text': '#31708f',
                'widget-bg': '#ffffff'
            }
        },
        'opts': {
            'app_search_desc': None,
            'notification_days': None,
            'disable_google_geocoder': True,
            'disable_social': None,
            'app_search_title': None,
            'forced_widget_page': None,
            'pdf_footer_center_html': None,
            'has_app': 1,
            'wizard_only': None,
            'consent_privacy_hide_question': None,
            'cookie_expires': None,
            'disable_print_download': None,
            'arcgis_geocoder': None,
            'pdf_header_center_html': None,
            'google_geocoder': None,
            'app_navigation_page2': 'app_navigation_tabs',
            'pdf_show_zones': None,
            'require_explicit_consent': None,
            'place_cookie': None,
            'hide_powered_by': None,
            'enable_wizard': True,
            'consent_privacy': None,
            'has_zone_reminders': None,
            'wizard_page': None,
            'pick_random_notification_day': None,
            'no_locale_picker': None,
            'mobile_reminder_zone_name': None,
            'pdf_header_center_html_zone_desc': None,
            'notify_delivery_offset': None,
            'has_available_app': True,
            'pdf_header_right_html': None,
            'allows_iframe': None,
            'ignore_late_delivery': None,
            'banner': {},
            'print_zones_in_calendar_pdf': None,
            'fix_nb_routes': None,
            'tabbed_widget': None,
            'wizard_locales': None,
            'disable_widget_app_buttons': None
        },
        'title': 'Solid Waste',
        'background_img': '',
        'default_page': 'calendar_search',
        'area': {
            'logo_alt_text': {},
            'id': 311,
            'bounds': '42.294403,-71.1788987|42.4181407,-71.0642633',
            'enable_sms': 1,
            'name': 'Boston',
            'title': 'City of Boston',
            'has_app': 1,
            'region': 'us',
            'has_logo': 1,
            'logo_img': {
                'en': '2D4F557A-B6DF-11E4-BC05-D2768E6A6F5F',
                'en-US': '2D4F557A-B6DF-11E4-BC05-D2768E6A6F5F'
            },
            'timezone': 'America/New_York',
            'twitter_userid': '222834003',
            'email_banner': {},
            'locales': ['en-US', 'es'],
            'default_locale': 'en-US',
            'enable_voice': 1,
            'account': {'id': 89},
            'twitter_screen_name': {'en': 'recollectnet'},
            'geocoder_suffix': 'Boston MA',
            'logo_url': 'http://www.cityofboston.gov/residents/PublicWorksAndUtilities.asp',
            'enable_twitter': 0
        },
        'mobile_app_name': 'Boston Trash Schedule & Alerts',
        'icon': 'recycle',
        'wizard_url': {
            'en-US': 'https://www.boston.gov/trash-day-schedule'},
        'sharing_msg': {},
        'design': 'default',
        'can_auto_translate': '1',
        'collection_time_msg': {'en-US': ''},
        'default_locale': 'en-US',
        'opts_checksum': 'fb12fbdc34a8e5b4f646278900f8ba1eba1b4d94ac868b58b96f77f8e92f7a66',
        'success_web_snippet': '',
        'full_name': 'Boston/waste',
        'email_style': {
            'Default': {
                'alert-info-bg': '#d9eef7',
                'btn-success-border': '#67BB4D',
                'navbar-default-border': '#67BB4D',
                'text-color': '#333333',
                'btn-success-bg': '#59A343',
                'btn-success-color': '#FFFFFF',
                'btn-default-border': '#cccccc',
                'btn-default-bg': '#FFFFFF',
                'link-hover-color': '#86c655',
                'link-color': '#508527',
                'btn-danger-border': '#bd362f',
                'btn-danger-color': '#FFFFFF',
                'alert-info-border': '#bce8f1',
                'widget-border': '#ececec',
                'calendar-border': '#dddddd',
                'navbar-default-bg': '#59A343',
                'btn-default-color': '#333333',
                'btn-danger-bg': '#ee5f5b',
                'alert-info-text': '#31708f',
                'widget-bg': '#ffffff'
            }
        },
        'widget_style': {
            'Default': {
                'alert-info-text': '#31708f',
                'widget-bg': '#ffffff',
                'btn-default-color': '#000000',
                'btn-danger-bg': '#e9170c',
                'calendar-border': '#dddddd',
                'navbar-default-bg': '#1c2936',
                'widget-border': '#ececec',
                'alert-info-border': '#bce8f1',
                'btn-danger-color': '#ffffff',
                'btn-danger-border': '#e9170c',
                'link-color': '#0033cc',
                'btn-default-border': '#3e738f',
                'custom_styles': '#rCw {\n    ul.dropdown-menu {\n        li {\n            list-style-type: none;\n        }\n    }\n}\n.rCw .fc-event {\n    font-size: 10.5px !important;\n}',
                'link-hover-color': '#0033cc',
                'btn-default-bg': '#ffffff',
                'btn-success-color': '#ffffff',
                'text-color': '#333333',
                'btn-success-bg': '#3e738f',
                'btn-success-border': '#3e738f',
                'navbar-default-border': '#1c2936',
                'alert-info-bg': '#d9eef7'
            }
        },
        'support_cc': '',
        'default_address': {
            'en': '1 City Hall Plz, Boston',
            'en-US': '1 City Hall Plz, Boston'
        }
    }
}




# Snow Emergency Parking Intent


CLOSEST_PARKING_DRIVING_DATA = [
    {
        'Driving distance': 12682,
        'Driving distance text': '7.9 mi',
        'Driving time': 1130,
        'Driving time text': '19 mins',
        'Address': '115 Harvard Ave Boston, MA'
    },
    {
        'Driving distance': 14653,
        'Driving distance text': '9.1 mi',
        'Driving time': 1271,
        'Driving time text': '21 mins',
        'Address': '398 Market St Boston, MA'
    },
    {
        'Driving distance': 11670,
        'Driving distance text': '7.3 mi',
        'Driving time': 1015,
        'Driving time text': '17 mins',
        'Address': '111 Western Ave Boston, MA'
    },
    {
        'Driving distance': 11586,
        'Driving distance text': '7.2 mi',
        'Driving time': 1507,
        'Driving time text': '25 mins',
        'Address': '1891 Centre Street Boston, MA'
    },
    {
        'Driving distance': 8846,
        'Driving distance text': '5.5 mi',
        'Driving time': 1022,
        'Driving time text': '17 mins',
        'Address': '39-41 Corey St Boston, MA'
    },
    {
        'Driving distance': 5438,
        'Driving distance text': '3.4 mi',
        'Driving time': 745,
        'Driving time text': '12 mins',
        'Address': '1 Avenue De Lafayette Boston, MA'
    }
]






CLOSEST_PARKING_MOCK_RETURN = {
    'Driving distance': 2458,
    'Driving distance text': '1.5 mi',
    'Driving time': 427,
    'Driving time text': '7 mins',
    'Parking Address': '94 Sawyer Ave Boston, MA'
}

GET_PARKING_DATA_MOCK_RETURN = [
    [
        1,
        1,
        60,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #003',
        '115 Harvard Ave',
        ' ',
        0,
        ' ',
        '1bc385c4-285f-49d6-a606-151380906d38',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7918414.198468381,
            'y': 5213945.511252668
        }
    ],
    [
        2,
        2,
        42,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #002',
        '398 Market St',
        ' ',
        0,
        ' ',
        'a9fcf634-ae60-407a-8b05-9bcac6bfeb63',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7920695.3886001585,
            'y': 5213501.824205618
        }
    ],
    [
        3,
        3,
        700,
        'No Charge',
        'Only Allston and Brighton residents can park at this garage during a snow emergency only. May need to show proof of residency. Parking spots are limited and on a first-come, first-served basis. If parked past the approved the time, may be ticketed/towed.',
        '617-496-6400',
        'Harvard University/Soldiers Field Park Garage at 111 Western Avenue',
        '111 Western Ave',
        ' ',
        0,
        ' ',
        '9e939045-7d01-4981-bd86-819eec93ec7c',
        1512407360712,
        'BostonGIS',
        1512767171796,
        '143525_boston', {
            'x': -7917328.721328608,
            'y': 5215701.113088339
        }
    ],
    [
        4,
        4,
        18,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #034',
        '1891 Centre Street',
        ' ',
        0,
        ' ',
        '0cddfbc4-5afb-40fb-a783-d9f98c95f3a7',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7921074.252411649,
            'y': 5203874.208464791
        }
    ],
    [
        5,
        5,
        53,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #010',
        '39-41 Corey St',
        ' ',
        0,
        ' ',
        '5379d27e-2f96-43ca-aea2-9810bad6ac36',
        1512407360712,
        'BostonGIS',
        1512408881834,
        '', {
            'x': -7920843.6752729565,
            'y': 5203887.009613773
        }
    ],
    [
        6,
        6,
        800,
        '$10 for each 24-hour period',
        'Discounted parking is only for Chinatown, Downtown, and North End residents. You need to provide proof of your residency. You will be charged each time your vehicle exits and re-enters the garage.',
        '617-357-1987',
        'Lafayette Garage',
        '1 Avenue De Lafayette',
        ' ',
        0,
        ' ',
        '6a6f6aba-32f9-4ed4-8faf-86b3527b017f',
        1512407360712,
        'BostonGIS',
        1515067413215,
        'BostonGIS', {
            'x': -7910585.48963993,
            'y': 5214061.022491527
        }
    ],
    [
        7,
        7,
        60,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #018',
        '450 West Broadway',
        ' ',
        0,
        ' ',
        '5f992294-e587-4cab-90ac-58e9b9e2765d',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7908861.051597621,
            'y': 5211509.010329823
        }
    ],
    [
        8,
        8,
        22,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #021',
        '650-652 East Broadway\r\n',
        ' ',
        0,
        ' ',
        '22459e32-8031-4d07-a2b3-37724ec6d665',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7907958.619185366,
            'y': 5211428.399287086
        }
    ],
    [
        9,
        9,
        1766,
        '$1 for each night',
        'The discount is only for South Boston with a Resident Parking permits sticker.  The garage only allows snow emergency parking on the fourth floor.',
        '617-482-2487',
        'BRA/EDIC Garage',
        '12 Drydock Ave',
        ' ',
        0,
        ' ',
        '6bd71b92-c461-4a3c-ad4a-9426fdc474b4',
        1512407360712,
        'BostonGIS',
        1512768444415,
        '143525_boston', {
            'x': -7907683.986350929,
            'y': 5212805.040508509
        }
    ],
    [
        10,
        10,
        864,
        'You pay 50% of the variable rate. The most you will pay is $17.50 for each 24-hour period.',
        'Discounted parking is for Roxbury, South End, and Fenway/Kenmore residents only. Need to have a visible resident parking permit sticker to receive the discount. Parking is based on a first-come basis and depends on the availability of space.',
        '617-267-9677',
        'Northeastern University/Renaissance Park Garage',
        '835 Columbus Avenue',
        ' ',
        0,
        ' ',
        '5053fd3b-4799-4027-94bc-947c69d25945',
        1512407360712,
        'BostonGIS',
        1513968972322,
        '', {
            'x': -7913403.170262766,
            'y': 5211611.002931875
        }
    ],
    [
        11,
        11,
        350,
        'You pay 50% of the variable rate. The most you will pay is $17.50 for each 24-hour period.',
        'Discounted parking is for Roxbury, South End, and Fenway/Kenmore residents only. Need to have a visible resident parking permit sticker to receive the discount. Parking is based on a first-come basis and depends on the availability of space.',
        '617-266-7260',
        'Northeastern University/Gainsboro Garage',
        '10 Gainsborough Street',
        ' ',
        0,
        ' ',
        '1cd2ff90-10cb-48d0-b77f-76b92cbba22e',
        1512407360712,
        'BostonGIS',
        1512768231449,
        '143525_boston', {
            'x': -7913221.157520119,
            'y': 5212108.194550944
        }
    ],
    [
        12,
        12,
        400,
        '$10/24 hrs',
        'Discounted parking is only for Back Bay, Beacon Hill, Chinatown, Downtown, Fenway/Kenmore, and South End residents. You will be charged each time you exit and re-enter the garage with your vehicle.',
        '617-247-8006',
        'Auditorium Garage',
        '50 Dalton St',
        ' ',
        0,
        ' ',
        '005a11ed-4a55-4373-b4b7-1cda6571e451',
        1512407360712,
        'BostonGIS',
        1512765941504,
        '143525_boston', {
            'x': -7913231.87034365,
            'y': 5213115.979027377
        }
    ],
    [
        13,
        13,
        250,
        'FULL',
        'Charlestown residents only.  Limited space so the garage enforces the 2 hour rule.  Anyone who enters more than 2 hours before the Snow Emergency is in effect and/or departs more than 2 hours after the ban has lifted, will not receive the discount rate.',
        ' ',
        'Shipyard Garage/Mass General Hospital',
        'Building #199 13th St\r\n',
        ' ',
        0,
        ' ',
        '4a6dd815-9a4a-48ab-b910-a688e451fd92',
        1512407360712,
        'BostonGIS',
        1520896459450,
        'mclane', {
            'x': -7909345.539839093,
            'y': 5217566.218936113
        }
    ],
    [
        15,
        15,
        42,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #017',
        '575-581 Washington St\r\n',
        ' ',
        0,
        ' ',
        'c2c0ebac-589d-468a-9ba8-cd9a8a8eff0a',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7911698.640175789,
            'y': 5204726.838356973
        }
    ],
    [
        16,
        16,
        100,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #019',
        '16 Hamlet St',
        ' ',
        0,
        ' ',
        'e95d9902-6513-4d26-bb9f-3d5579f5e320',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7910949.366851533,
            'y': 5208745.364755854
        }
    ],
    [
        17,
        17,
        22,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #020 \r\n',
        '191 Adams St',
        ' ',
        0,
        ' ',
        '2849c5ff-fcc8-4d56-b667-1454c6d222da',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7910427.297246154,
            'y': 5206386.200671472
        }
    ],
    [
        18,
        18,
        12,
        'No Charge',
        ' ',
        ' ',
        'Municipal Lot #022',
        '730-732 Dudley St',
        ' ',
        0,
        ' ',
        '7035791d-a24a-4811-a077-2aff4bb74e15',
        1512407360712,
        'BostonGIS',
        1512407360712,
        'BostonGIS', {
            'x': -7911151.4108671965,
            'y': 5208755.251808084
        }
    ]
]


# get_alerts intent

GET_ALERTS_MOCK_NO_ALERTS = {
    'Alert header': '',
    'City building hours': 'All municipal buildings are open based on their normal hours.',
    'Parking meters': 'Parking meters are running on their normal schedules today.',
    'Street Cleaning': 'Today is the first Thursday of the month and street cleaning is running on a normal schedule.',
    'Tow lot': 'The tow lot is open from 7 a.m. - 11 p.m. Automated kiosks are available 24 hours a day, seven days a week for vehicle releases.',
    'Trash and recycling': 'Pickup is on a normal schedule.'
}

GET_ALERTS_MOCK_SOME_ALERTS = {
    'Tow lot': 'Tow lots destroyed!', 'Parking meters': 'Parking meters are all broken.',
    'City building hours': 'Stay away from city buildings.',
    'Trash and recycling': 'Pickup is on a normal schedule.',
    'Street Cleaning': 'Street cleaning is canceled',
    'Alert header': 'Godzilla inbound!'
}

# get_open_spaces intent

OPEN_SPACES_TEST_CSV =  os.getcwd() + "/mycity/test/test_data/.csv"

CLOSEST_OPEN_SPACES_DRIVING_DATA = \
    [
        {
            'Driving distance text': '7.9 mi',
            'Driving distance': 12682,
            'Driving time text': '19 mins',
            'Driving time': 1130,
            'Parking Lot': '115 Harvard Ave Boston, MA'
        },
        {
            'Driving distance text': '9.1 mi',
            'Driving distance': 14653,
            'Driving time text': '21 mins',
            'Driving time': 1271,
            'Parking Lot': '398 Market St Boston, MA'
        },
        {
            'Driving distance text': '7.3 mi',
            'Driving distance': 1,
            'Driving time text': '17 mins',
            'Driving time': 1,
            'Parking Lot': '536 Commericial Str., Boston, MA'
        }
    ]
