"""Mock objects for the API tests."""


mock_data_no_hints_no_metadata = {
    "hints": [],
    "records": [
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2010, "value": 88.2, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2012, "value": 83, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2014, "value": 86.77, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2015, "value": 88.07, "magnitude": None, "qualifier": None},
    ],
    "indicatorMetadata": []
}

mock_data_no_hints_with_metadata = {
    "hints": [],
    "records": [
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2010, "value": 88.2, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2012, "value": 83, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2014, "value": 86.77, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2015, "value": 88.07, "magnitude": None, "qualifier": None},
    ],
    "indicatorMetadata": [
        {"indicatorCode": "CR.1",
         "name": "Completion rate, primary education, both sexes (%)",
         "theme": "EDUCATION",
         "lastDataUpdate": "2024-10-29",
         "lastDataUpdateDescription": "September 2024 Data Release",
         "glossaryTerms": [{"themes": ["EDUCATION"],"termId": 3201,"language": "en", "name": "Completion rate"}],
         "disaggregations": [{"code": "EduLvl:ISCED1",
                              "name": "ISCED 1 - Primary education",
                              "glossaryTerms": [{"themes": ["EDUCATION"],"termId": 2066,"language": "en","name": "ISCED 1: Primary education",}],
                              "disaggregationType": {"code": "EduLvl","name": "Education Level","glossaryTerms": []}
                              }],
         "dataAvailability": {"totalRecordCount": 2025,"timeLine": {"min": 1996,"max": 2023},
                              "geoUnits": {"types": ["NATIONAL","REGIONAL"]}
                              }
        }
    ]
}


mock_data_hints_no_metadata = {
    "hints": [{"code": "UIS::HINT::001","message": "The indicator could not be found, invalid"}],
    "records": [
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2010, "value": 88.2, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2012, "value": 83, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2014, "value": 86.77, "magnitude": None, "qualifier": None},
        {"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2015, "value": 88.07, "magnitude": None, "qualifier": None},
    ],
    "indicatorMetadata": []
}