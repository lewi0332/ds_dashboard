from dash import html, dcc
import dash_bootstrap_components as dbc


# Dummy page to get started.
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                dcc.Markdown(id='intro',
                children = """
                ---
                # The Data Science Job Hunt
                ---
                
                In 2025 finding a data science job is a challenge. LinkedIn feels like the hunger games. Tech layoffs are
                common, and after a solid decade of "Data Science" being the sexiest job of the 21st century, the market is
                saturated with candidates and the competition is fierce. Additionally, company leaders are skeptical of the
                value of data science and are waiting to see how Large Language Models (LLM) will change the game. From my
                perspective, the data science field is in its donut phase: There are roles for analysts and roles for PhDs, 
                but the middle is missing.

                
                What better way to find a data science role then to use data science. This is a simple tool to help me do that. 
                Consider it a small portfolio project to demonstrate an ability to gather, query, present track and predict 
                data. All while actully providing me with a useful tool to help find a job.

                ---
                """,
                className='card-text',
                ),
            ]
        )
    ]),
    dbc.Row(
        [
        # dbc.Col(width=1),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardImg(src="/static/images/channel.png", top=True, style={'opacity': '0.05'}),
                    dbc.CardImgOverlay([
                    dbc.CardBody(
                        [
                            dcc.Markdown("""
                            ---
                            # Dashboard
                            ---

                            Tracking the jobs I've applied to, the interviews I've had, and the offers I've received.
                            """,
                            className='card-text',
                            ),
                        ],
                    ),
                    dbc.Button(
                        'View Page',
                        href='/dashboard',
                        class_name='view-page-button-style',
                        style={'position': 'absolute', 'bottom': '10px'}
                    ),]
                    ),
                ]
            ),
            width=6
        ),
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardImg(src="static/images/cover_letter.png", top=True, style={'opacity': '0.05'},
                                ),
                    dbc.CardImgOverlay([
                        dbc.CardBody(
                            dcc.Markdown("""
                                ---
                                ## Cover Letter Generator
                                ---
                                        
                                If the job market is using software to filter my resumes, why
                                not use software to generate cover letters
                                
                                If this seem like cheating to you, you're probably not looking to hire
                                a data scientist who can write code to automate tasks.
                                """,
                                className='card-text',
                                )
                            ),
                        dbc.Button(
                            'View Page',
                            href='/cover-letter',
                            class_name='view-page-button-style',
                            style={'position': 'absolute', 'bottom': '10px'}
                            )
                    ])
                ]
            )], 
            width=6
        )]
    ),
    html.Br(),
    html.Br(),
    dbc.Row(
        [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardImg(src="static/images/segmentation.png", top=True, style={'opacity': '0.05'}),
                    dbc.CardImgOverlay([
                        dbc.CardBody(
                            dcc.Markdown("""
                        ---
                        # Segmentation
                        ---

                        Coming soon: Using segmentation methods to identify segments of the job market and 
                        how they respond to my applications. 
                        """,
                        className='card-text',
                            )
                        ),
                        dbc.Button(
                            'View Page', 
                            href='/Q3',
                            class_name='view-page-button-style',
                            style={'position': 'absolute', 'bottom': '10px'}
                        )]
                    )
                ]
            ),
            width=6
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardImg(src="static/images/about_me.png", top=True, style={'opacity': '0.05'}),
                    dbc.CardImgOverlay([
                        dbc.CardBody(
                            dcc.Markdown("""
                                ---
                                # About Me
                                ---

                                Data Science is a wide field. In my own words, heres a bit about me and
                                my particular niche in the field.
                                """,
                                className='card-text',
                                ),
                            ),
                        dbc.Button(
                            'View Page', 
                            href='/Q3',
                            class_name='view-page-button-style',
                            style={'position': 'absolute', 'bottom': '10px'}
                            )
                        ]
                    )
                ]
            ),
            width=6
        ),
        ]

    )
])
