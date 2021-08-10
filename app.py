import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
# Reasonable ordering
gss_clean["satjob"] = gss_clean["satjob"].astype("category").cat.reorder_categories(["very satisfied", "mod. satisfied", "a little dissat", "very dissatisfied"])
gss_clean["relationship"] = gss_clean["relationship"].astype('category').cat.reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])
gss_clean["male_breadwinner"] = gss_clean["male_breadwinner"].astype('category').cat.reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])
gss_clean["men_bettersuited"] = gss_clean["men_bettersuited"].astype('category').cat.reorder_categories(['agree', 'disagree'])
gss_clean["child_suffer"] = gss_clean["child_suffer"].astype('category').cat.reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])
gss_clean["men_overwork"] = gss_clean["men_overwork"].astype('category').cat.reorder_categories(['strongly agree', 'agree', 'neither agree nor disagree', 'disagree', 'strongly disagree'])


gwg_description = '''
Gender wage gap refers to the differences in wages between men and women. It has been known that women 
consistently earn less than men. Gender wage gap is caused by a number of reasons, including but not 
limited to differences in industry sectors, differences in working experience, differences in working time,
and discrimination.

Sources: [americanprogress.org](https://www.americanprogress.org/issues/women/reports/2020/03/24/482141/quick-facts-gender-wage-gap/)'''

gss_description = '''
The General Social Survey (GSS) is a representative survey of adults in the United States, 
and the main goal of the survey is to monitor and explain trends in attitudes, behaviors and opinions. 
Questions in GSS consist of 2 components, covering both standard demographic questions and topics of special interest.
GSS data are easily accessible and often with minimal cost.

Sources: [GSS website](http://www.gss.norc.org/About-The-GSS)'''


my_table2 = gss_clean.groupby("sex").agg({"income": "mean", "job_prestige": "mean", 
                                         "socioeconomic_index": "mean", "education": "mean"}).reset_index().round(2)
my_table2.rename(columns={"sex": "Sex",
                         "income": "Mean Annual Income (USD)",
                         "job_prestige": "Mean Occupational Prestige",
                         "socioeconomic_index": "Mean Socioeconomic Index",
                         "education": "Mean Years of Education"}, inplace=True)
table2 = ff.create_table(my_table2)


my_table = gss_clean.groupby(["sex", "male_breadwinner"]).size().reset_index().rename(columns={0: "size"})
fig3 = px.bar(my_table, x="male_breadwinner", y="size", color="sex", labels={'male_breadwinner': 'Level of agreement', 'size':'Number of responses', 'sex': 'Sex'})
fig3.update(layout=dict(title=dict(x=0.5)))


fig4 = px.scatter(gss_clean, x="job_prestige", y="income", color="sex", trendline='ols',
                  opacity=0.5, hover_data=['education', 'socioeconomic_index'],
                  labels={"job_prestige": "Occupational prestige", "income": "Annual income", 
                          "education": "Years of Education", "socioeconomic_index": "Socioeconomic index",
                          "sex": "Sex"})
fig4.update(layout=dict(title=dict(x=0.5)))


fig5a = px.box(gss_clean, x='sex', y='income', labels={'income': 'Annual income', 'sex': ''})
fig5a.update(layout=dict(title=dict(x=0.5)))
fig5a.update_layout(showlegend=False)
fig5b = px.box(gss_clean, x='sex', y='job_prestige', labels={'job_prestige': 'Occupational prestige', 'sex': ''})
fig5b.update(layout=dict(title=dict(x=0.5)))
fig5b.update_layout(showlegend=False)


my_df = gss_clean[["income", "sex", "job_prestige"]]
my_df["job_prestige_level"] = pd.cut(my_df["job_prestige"], bins=6, labels=['Lowest', 'Low', 'Medium', 'Medium high', 'High', 'Highest'])
my_df.dropna(inplace=True)
my_df.sort_values(by='job_prestige_level', inplace=True)
fig6 = px.box(my_df, x='sex', y='income', color='sex', color_discrete_map = {'male':'blue', 'female':'red'}, facet_col='job_prestige_level', facet_col_wrap=2,
              labels={"job_prestige_level": "Occupational prestige", "income": "Annual income", "sex": "Sex"})



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring Gender Wage Gap through the General Social Survey"),
        html.H2("Introduction"),
        html.Div([html.H3("What is Gender Wage Gap ?"), dcc.Markdown(children=gwg_description)], style={'width':'49%', 'float':'left'}),
        html.Div([html.H3("What is the General Social Survey ?"), dcc.Markdown(children=gss_description)], style={'width':'49%', 'float':'right'}),
        html.Div([html.H2("Mean Annual Income (USD), Occupational Prestige, Socioeconomic Index and Years of Education, for Men and Women"), dcc.Graph(figure=table2)], style={'width':'60%', 'float':'left'}),
        html.Div([html.H2("Survey Responses Explorer"),
                  html.H3("Survey Question:"),
                  dcc.Dropdown(id='quest',
                               options=[{'label': "On the whole, how satisfied are you with the work you do?", 'value': "satjob"},
                                        {'label': "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work.", 'value': "relationship"},
                                        {'label': "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.", 'value': "male_breadwinner"},
                                        {'label': "Most men are better suited emotionally for politics than are most women.", 'value': "men_bettersuited"},
                                        {'label': "A preschool child is likely to suffer if his or her mother works.", 'value': "child_suffer"},
                                        {'label': "Family life often suffers because men concentrate too much on their work.", 'value': "men_overwork"}],
                               value='male_breadwinner'),
                  html.H3("Group by:"),
                  dcc.Dropdown(id='group',
                               options=[{'label': "Sex", 'value': "sex"},
                                        {'label': "Region", 'value': "region"},
                                        {'label': "Years of Education", 'value': "education"}],
                               value='sex'),
                  dcc.Graph(id="graph")], style={'width':'40%', 'float':'right'}),
        html.Div([html.H2("Occupational Prestige versus Annual Income, for Men and Women"), dcc.Graph(figure=fig4)], style={'width':'50%'}), 
        html.H2("Annual Income and Occupational Prestige, for Men and Women"),
        html.Div([dcc.Graph(figure=fig5a)], style={'width':'48%', 'float':'left'}),
        html.Div([dcc.Graph(figure=fig5b)], style={'width':'48%', 'float':'right'}),
        html.H2("Annual Income for Men and Women, by Occupational Prestige Level"),
        dcc.Graph(figure=fig6)
    ]
)

@app.callback(Output(component_id="graph",component_property="figure"), 
             [Input(component_id='quest',component_property="value"),
              Input(component_id='group',component_property="value")])
def make_figure(quest, group):
    my_table = gss_clean.groupby([group, quest]).size().reset_index().rename(columns={0: "size"})
    return px.bar(my_table, x=quest, y="size", color=group, labels={quest: 'Level of agreement', 'size':'Number of responses'})

if __name__ == '__main__':
    app.run_server(debug=True)
