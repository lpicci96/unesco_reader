"""Mock objects for the API tests."""

mock_data_no_hints_no_metadata = {
    "hints": [],
    "records": [
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2010,
            "value": 88.2,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2012,
            "value": 83,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2014,
            "value": 86.77,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2015,
            "value": 88.07,
            "magnitude": None,
            "qualifier": None,
        },
    ],
    "indicatorMetadata": [],
}

mock_data_no_hints_metadata = {
    "hints": [],
    "records": [
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2010,
            "value": 88.2,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2012,
            "value": 83,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2014,
            "value": 86.77,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2015,
            "value": 88.07,
            "magnitude": None,
            "qualifier": None,
        },
    ],
    "indicatorMetadata": [
        {
            "indicatorCode": "CR.1",
            "name": "Completion rate, primary education, both sexes (%)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "glossaryTerms": [
                {
                    "themes": ["EDUCATION"],
                    "termId": 3201,
                    "language": "en",
                    "name": "Completion rate",
                }
            ],
            "disaggregations": [
                {
                    "code": "EduLvl:ISCED1",
                    "name": "ISCED 1 - Primary education",
                    "glossaryTerms": [
                        {
                            "themes": ["EDUCATION"],
                            "termId": 2066,
                            "language": "en",
                            "name": "ISCED 1: Primary education",
                        }
                    ],
                    "disaggregationType": {
                        "code": "EduLvl",
                        "name": "Education Level",
                        "glossaryTerms": [],
                    },
                }
            ],
            "dataAvailability": {
                "totalRecordCount": 2025,
                "timeLine": {"min": 1996, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        }
    ],
}

mock_data_hints_no_metadata = {
    "hints": [
        {
            "code": "UIS::HINT::001",
            "message": "The indicator could not be found, invalid",
        }
    ],
    "records": [
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2010,
            "value": 88.2,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2012,
            "value": 83,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2014,
            "value": 86.77,
            "magnitude": None,
            "qualifier": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2015,
            "value": 88.07,
            "magnitude": None,
            "qualifier": None,
        },
    ],
    "indicatorMetadata": [],
}


mock_no_data_hints = {
    "hints": [
        {
            "code": "UIS::HINT::001",
            "message": "The indicator could not be found, invalid",
        }
    ],
    "records": [],
    "indicatorMetadata": [],
}

mock_no_data_multiple_hints = {
    "hints": [
        {
            "code": "UIS::HINT::001",
            "message": "The indicator could not be found, invalid 1",
        },
        {
            "code": "UIS::HINT::002",
            "message": "The indicator could not be found, invalid 2",
        },
    ],
    "records": [],
    "indicatorMetadata": [],
}


mock_data_footnotes = [
    {
        "indicatorId": "CR.1",
        "geoUnit": "AFG",
        "year": 2011,
        "value": 1,
        "magnitude": None,
        "qualifier": None,
        "footnotes": [
            {"type": "Source", "subtype": "Data sources", "value": "some footnote"}
        ],
    },
    {
        "indicatorId": "CR.1",
        "geoUnit": "AFG",
        "year": 2015,
        "value": 2,
        "magnitude": None,
        "qualifier": None,
        "footnotes": [],
    },
    {
        "indicatorId": "CR.1",
        "geoUnit": "AFG",
        "year": 2022,
        "value": 3,
        "magnitude": None,
        "qualifier": None,
        "footnotes": [
            {"type": "Source", "subtype": "Data sources", "value": "footnote 1"},
            {"type": "Category", "subtype": "Subcategory", "value": "footnote 2"},
        ],
    },
]


mock_indicators_no_agg_no_glossary = [
    {
        "indicatorCode": "10",
        "name": "Official entrance age to early childhood educational development (years)",
        "theme": "EDUCATION",
        "lastDataUpdate": "2024-10-29",
        "lastDataUpdateDescription": "September 2024 Data Release",
        "dataAvailability": {
            "totalRecordCount": 4675,
            "timeLine": {"min": 1970, "max": 2023},
            "geoUnits": {"types": ["NATIONAL"]},
        },
    },
    {
        "indicatorCode": "10403",
        "name": "Start month of the academic school year (tertiary education)",
        "theme": "DEMOGRAPHICS",
        "lastDataUpdate": "2010-10-29",
        "lastDataUpdateDescription": "September 2024 Data Release",
        "dataAvailability": {
            "totalRecordCount": 5192,
            "timeLine": {"min": 1991, "max": 2023},
            "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
        },
    },
]

mock_geo_units = [
    {"id": "ABW", "name": "Aruba", "type": "NATIONAL"},
    {"id": "AFG", "name": "Afghanistan", "type": "NATIONAL"},
    # {'id': 'ALECSO: Mashriq countries', 'name': 'Mashriq countries','type': 'REGIONAL'},
    {"id": "UNESCO: SIDS", "name": "SIDS", "type": "REGIONAL", "regionGroup": "UNESCO"},
]


mock_list_versions = [
    {
        "version": "20241030-9d4d089e",
        "publicationDate": "2024-10-30T17:28:00.868Z",
        "description": "Drop data for CIV on MYS for 1988 and 1998 and update some other education datapoints",
        "themeDataStatus": [
            {
                "theme": "EDUCATION",
                "lastUpdate": "2024-10-29",
                "description": "September 2024 Data Release",
            },
            {
                "theme": "SCIENCE_TECHNOLOGY_INNOVATION",
                "lastUpdate": "2024-02-24",
                "description": "February 2024 Data Release",
            },
            {
                "theme": "CULTURE",
                "lastUpdate": "2023-11-25",
                "description": "November 2023 Data Release",
            },
            {
                "theme": "DEMOGRAPHIC_SOCIOECONOMIC",
                "lastUpdate": "2024-10-29",
                "description": "September 2024 Data Release",
            },
        ],
    },
    {
        "version": "20240913-b8ca1963",
        "publicationDate": "2024-09-15T14:44:07.750Z",
        "description": "Glossary Update",
        "themeDataStatus": [
            {
                "theme": "EDUCATION",
                "lastUpdate": "2024-09-05",
                "description": "September 2024 Data Release",
            },
            {
                "theme": "SCIENCE_TECHNOLOGY_INNOVATION",
                "lastUpdate": "2024-02-28",
                "description": "February 2024 Data Release",
            },
            {
                "theme": "CULTURE",
                "lastUpdate": "2023-11-25",
                "description": "November 2023 Data Release",
            },
            {
                "theme": "DEMOGRAPHIC_SOCIOECONOMIC",
                "lastUpdate": "2024-09-05",
                "description": "September 2024 Data Release",
            },
        ],
    },
    {
        "version": "20240910-b5ad4d82",
        "publicationDate": "2024-09-11T06:15:13.018Z",
        "description": "September 2024 Data Release (first data publication via API)",
        "themeDataStatus": [
            {
                "theme": "EDUCATION",
                "lastUpdate": "2024-09-05",
                "description": "September 2024 Data Release",
            },
            {
                "theme": "SCIENCE_TECHNOLOGY_INNOVATION",
                "lastUpdate": "2024-02-28",
                "description": "February 2024 Data Release",
            },
            {
                "theme": "CULTURE",
                "lastUpdate": "2023-11-25",
                "description": "November 2023 Data Release",
            },
            {
                "theme": "DEMOGRAPHIC_SOCIOECONOMIC",
                "lastUpdate": "2024-09-05",
                "description": "September 2024 Data Release",
            },
        ],
    },
]


mock_default_version = {
    "version": "20241030-9d4d089e",
    "publicationDate": "2024-10-30T17:28:00.868Z",
    "description": "Drop data for CIV on MYS for 1988 and 1998 and update some other education datapoints",
    "themeDataStatus": [
        {
            "theme": "EDUCATION",
            "lastUpdate": "2024-10-29",
            "description": "September 2024 Data Release",
        },
        {
            "theme": "SCIENCE_TECHNOLOGY_INNOVATION",
            "lastUpdate": "2024-02-24",
            "description": "February 2024 Data Release",
        },
        {
            "theme": "CULTURE",
            "lastUpdate": "2023-11-25",
            "description": "November 2023 Data Release",
        },
        {
            "theme": "DEMOGRAPHIC_SOCIOECONOMIC",
            "lastUpdate": "2024-10-29",
            "description": "September 2024 Data Release",
        },
    ],
}
