from dash import html, dcc, register_page, callback
import dash_mantine_components as dmc


register_page(__name__, path='/')

card_style = {
    "border": f"1px solid {dmc.DEFAULT_THEME['colors']['indigo'][4]}",
    "textAlign": "center",
}

layout = dmc.Container([
    dcc.Markdown(id='home_intro',
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

        Would you like me to build you a tool like this? Obviously, I'm looking for a job, so I'm open to freelance work.

        Let's connect:

        > [LinkedIn](https://www.linkedin.com/in/derrickjlewis/)

        > [www.derrickjlewis.com](https://www.derrickjameslewis.com/)

        > [GitHub](https://github.com/lewi0332)

        ---
        """,
        className='card-text',
    ),
    dmc.Grid(
        gutter='xl',  
        justify='space-around',
        children=[
            dmc.GridCol(
                dmc.Card(
                    children = [
                        dmc.CardSection(
                            dmc.BackgroundImage(
                                src="/static/images/channel.png",
                                children = [
                                    dmc.Center(
                                        children=[
                                            dmc.Stack(
                                                className='card-text',
                                                children=[
                                                    dcc.Markdown("""
                                                                 ---
                                                                 ## Dashboard
                                                                 ---
                                                                 Tracking the jobs I've applied to, the interviews I've had, and the offers I've received.
                                                                """,
                                                    className='card-text',
                                                    ),
                                                ]
                                            )
                                        ],
                                        # w=600,
                                        # h=600,
                                        p="md",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.9)", "width": "100%", "height": "100%", "display": "flex", "alignItems": "flex-start", "justifyContent": "flex-start"},                                    )
                                ],
                                w=600,
                                h=600,
                                style={"backgroundSize": "cover", "backgroundPosition": "center", "width": "100%", "height": "100%"}
                            ),
                        ),
                        dmc.Anchor(
                            dmc.Button('View Page'),
                            href='/dashboard'
                        )
                    ],
                    style={"display": "flex", "flexDirection": "column", "justifyContent": "space-between"},
                    p='xl',
                    # w=600,
                    # h=600,
                    shadow="sm",
                    withBorder=True,
                    radius="xl",
                ),
            span=5,
            ),
            dmc.GridCol(
                dmc.Card(
                    children = [
                        dmc.CardSection(
                            dmc.BackgroundImage(
                                src="/static/images/cover_letter.png",
                                children = [
                                    dmc.Center(
                                        children=[
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
                                            style={'justifyContent': 'top'},
                                            )
                                        ],
                                        p="md",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.9)", "width": "100%", "height": "100%", "display": "flex", "alignItems": "flex-start", "justifyContent": "flex-start"},
                                        # w=600,
                                        # h=600,
                                    )
                                ],
                                w=600,
                                h=600,
                                style={"backgroundSize": "cover", "backgroundPosition": "center", "width": "100%", "height": "100%"},
                            ),
                        ),
                        dmc.Anchor(
                            dmc.Button('View Page'),
                            href='/cover-letter'
                        )
                    ],
                    style={"display": "flex", "flexDirection": "column", "justifyContent": "space-between"},
                    p='xl',
                    # w=600,
                    # h=700,
                    shadow="sm",
                    withBorder=True,
                    radius="xl",
                ),
            span=5,
            ),
            dmc.GridCol(
                dmc.Card(
                    children = [
                        dmc.CardSection(
                            dmc.BackgroundImage(
                                src="/static/images/segmentation.png",
                                children = [
                                    dmc.Center(
                                        children=[
                                            dcc.Markdown("""
                                                ---
                                                ## Segmentation
                                                ---

                                                Coming soon: Using segmentation methods to identify segments of the job market and 
                                                how they respond to my applications.
                                                """,
                                            className='card-text',
                                            )
                                        ],
                                        p="md",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.9)", "width": "100%", "height": "100%", "display": "flex", "alignItems": "flex-start", "justifyContent": "flex-start"},
                                        # w=600,
                                        # h=600,
                                    )
                                ],
                                w=600,
                                h=600,
                                style={"backgroundSize": "cover", "backgroundPosition": "center", "width": "100%", "height": "100%"},
                            ),
                        ),
                        dmc.Anchor(
                            dmc.Button('View Page'),
                            href='/segmentation'
                        )
                    ],
                    style={"display": "flex", "flexDirection": "column", "justifyContent": "space-between"},
                    p='xl',
                    # w=600,
                    # h=700,
                    shadow="sm",
                    withBorder=True,
                    radius="xl",
                ),
            span=5,
            ),
            dmc.GridCol(
                dmc.Card(
                    children = [
                        dmc.CardSection(
                            dmc.BackgroundImage(
                                src="/static/images/about_me.png",
                                children = [
                                    dmc.Center(
                                        children=[
                                            dcc.Markdown("""
                                                ---
                                                ## About Me
                                                ---

                                                Data Science is a wide field. In my own words, heres a bit about me and
                                                my particular niche in the field.
                                                """,
                                            className='card-text',
                                            )
                                        ],
                                        p="md",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.9)", "width": "100%", "height": "100%", "display": "flex", "alignItems": "flex-start", "justifyContent": "flex-start"},
                                        # w=600,
                                        # h=600,
                                    )
                                ],
                                w=600,
                                h=600,
                                style={"backgroundSize": "cover", "backgroundPosition": "center", "width": "100%", "height": "100%"},
                            ),
                        ),
                        dmc.Anchor(
                            dmc.Button('View Page'),
                            href='/about'
                        )
                    ],
                    style={"display": "flex", "flexDirection": "column", "justifyContent": "space-between"},
                    p='xl',
                    # w=600,
                    # h=700,
                    shadow="sm",
                    withBorder=True,
                    radius="xl",
                ),
            span=5,
            ),
        ]
    ),
],
fluid=True
)
