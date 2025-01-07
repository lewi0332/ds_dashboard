from dash.dash_table import FormatTemplate as FormatTemplate


defaultColDef = {
#  "filter": "agNumberColumnFilter",
"enableCellTxtSelection": True,
"ensureDomOrder": True,
 "resizable": True,
 "sortable": True,
 "editable": False,
#  "floatingFilter": True,
}

JOBcolumnDefs =[
    {'headerName': 'Job Details', 'children': [
        {'headerName': 'App Date', 'field': 'application_date', 'filter': 'agDateColumnFilter'},
        {'headerName': 'Company', 'field': 'company_name', 'filter': 'agTextColumnFilter', 'minWidth': 150},
        {'headerName': 'Job Title', 'field': 'job_title', 'filter': 'agTextColumnFilter', 'minWidth': 200},
        {'headerName': 'Location', 'field': 'location', 'filter': 'agTextColumnFilter'},
        {'headerName': 'In-Office?', 'field': 'office_participation', 'filter': 'agTextColumnFilter'},
        {'headerName': 'Role', 'field': 'role_desc', 'filter': 'agTextColumnFilter', 'minWidth': 300},
        {'headerName': 'Responsibilities', 'field': 'responsibilities', 'filter': 'agTextColumnFilter', 'minWidth': 300},
        {'headerName': 'Requirements', 'field': 'requirements', 'filter': 'agTextColumnFilter', 'minWidth': 300},
        {'headerName': 'Pay Min', 'field': 'pay_min', 'filter': 'agNumberColumnFilter', 'cellStyle': {'textAlign': 'center'}, 'headerClass': 'center-aligned-header'},
        {'headerName': 'Pay Max', 'field': 'pay_max', 'filter': 'agNumberColumnFilter', 'cellStyle': {'textAlign': 'center'}, 'headerClass': 'center-aligned-header'},
    ]},
    {'headerName': 'Assesment', 'children': [
        {'headerName': 'Self Assessment', 'field': 'self_assessment', 'filter': 'agNumberColumnFilter', 'cellStyle': {'textAlign': 'center'}, 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Core Skills', 'field': 'core_skills', 'filter': 'agTextColumnFilter'},
        {'headerName': 'llm', 'field': 'llm', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'mmm', 'field': 'mmm', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'marketing', 'field': 'marketing', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Retail', 'field': 'retail', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Healthcare', 'field': 'healthcare', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Finance', 'field': 'finance', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Senior Role', 'field': 'senior_role', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Staff Role', 'field': 'staff_role', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Generalist Role', 'field': 'generalist_role', 'filter': 'agNumberColumnFilter',   'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
        {'headerName': 'Management Role', 'field': 'management_role', 'filter': 'agNumberColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header', 'maxWidth': 100},
    ]},
    {'headerName': 'Response', 'children': [        
        {'headerName': 'Recruiter Screen', 'field': 'recruiter_screen', 'filter': 'agNumberColumnFilter',  'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header'},
        {'headerName': 'Recruiter Screen Date', 'field': 'recruiter_screen_date', 'filter': 'agDateColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
        {'headerName': 'hiring_manager_screen', 'field': 'hiring_manager_screen', 'filter': 'agNumberColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header'},
        {'headerName': 'hiring_manager_screen_date', 'field': 'hiring_manager_screen_date', 'filter': 'agDateColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
        {'headerName': 'technical_screen', 'field': 'technical_screen', 'filter': 'agNumberColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header'},
        {'headerName': 'technical_screen_date', 'field': 'technical_screen_date', 'filter': 'agDateColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
        {'headerName': 'technical_screen_type', 'field': 'technical_screen_type', 'filter': 'agTextColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
        {'headerName': 'technical_screen_time', 'field': 'technical_screen_time', 'filter': 'agTextColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
        {'headerName': 'offer', 'field': 'offer', 'filter': 'agNumberColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header'},
        {'headerName': 'offer_date', 'field': 'offer_date', 'filter': 'agDateColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
        {'headerName': 'rejection', 'field': 'rejection', 'filter': 'agNumberColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header'},
        {'headerName': 'rejection_date', 'field': 'rejection_date', 'filter': 'agDateColumnFilter', 'cellClass': 'cellCenter', 'headerClass': 'center-aligned-header','columnGroupShow': 'open'},
    ],
    'columnGroupShow': 'open',
    },
    ]

column_size_options={
                'columnLimits': [
                    {'key': 'Role', 'minWidth': 900}],
            }

get_row_style = {
    "styleConditions": [
        {
            "condition": "params.data.rejection == 1",
            "style": {"backgroundColor": "rgba(240, 128, 128, 0.3)"},
        },
        {
            "condition": "params.data.hiring_manager_screen == 1",
            "style": {"backgroundColor": "rgba(0, 203, 166, 0.3)"},
        },
    ],
    # "defaultStyle": {"backgroundColor": "grey", "color": "white"},
}