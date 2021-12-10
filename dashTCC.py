import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import os, pymongo, numpy, asyncio
from dash.dependencies import Input, Output, State

BS = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"

app = dash.Dash(external_stylesheets=[BS])

colors = {
    'background': '#fff',
    'text': '#111111'
}

#Generating Screen
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Header(
        children='Análise das avaliações',
        style={
            'color': '#fff',
            'backgroundColor': '#3b2cbf',
            'border': '2px solid #1e175c',
            'padding': '10px',
            'textAlign': 'center',
            'fontSize': '25px',
            'fontFamily': 'Verdana',
            'width': '100%',
        }
    ),
    html.Div(
        [
            dcc.Input(id="input-on-submit", type="text", placeholder="Insira a url", 
                style={
                    'marginLeft':'50px', 
                    'marginTop': '20px', 
                    'width': '30%',
                    'padding': '6px 5px',
                    'border': '2px solid #1e175c',
                    'border-radius': '6px',
                }
            ),
            html.Button('Enviar', id='submit-val',
                style={
                    'color': '#fff',
                    'backgroundColor': '#3b2cbf',
                    'marginLeft': '8px',
                    'border': '2px solid #1e175c',
                    'border-radius': '8px',  
                }
            ),
            html.Div(id='container-button-basic',children='')
        ]    
    ),
])


@app.callback(
    Output('container-button-basic', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value')
)
def update_output(n_clicks, value):
    link = value
    print(link)
    #CONNECTION MONGO_DB
    MONGO_DATABASE = "crawler"
    client = pymongo.MongoClient("mongodb+srv://myCrawler:myCrawler209@clusternotices.rwnvw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client[MONGO_DATABASE]
    collection_notice = 'notices_collection'
    collection_rating = 'notices_rating'

    #Colors
    colors_pizza = ("#1e175c", "#3b2cbf",'#6357d4', "#978df0")
    colors_bar=("#ccc","#1e175c", "#1e175c" )


    #GetNoticeDatas
    #link = "https://www.terra.com.br/noticias/brasil/politica/eduardo-bolsonaro-testa-positivo-para-covid-na-volta-dos-eua,c530a3d8721800e2b07089eccd99174ebrkmp2yz.html"
    notFound = False


    #Get Specific Data
    try:
        rates = db[collection_rating].find({"link": link})
        rates = [rate_actual for rate_actual in rates]
        rate_actual = list(map(lambda x: x['rate_average'] , rates))
        rate_actual = rate_actual[0]
        numVotos = list(map(lambda x: x['numVotos'] , rates))
        numVotos = numVotos[0]
        rate_one = list(map(lambda x: x['rate_one'] , rates))
        rate_one = rate_one[0]
        rate_two = list(map(lambda x: x['rate_two'] , rates))
        rate_two = rate_two[0]
        rate_tree = list(map(lambda x: x['rate_tree'] , rates))
        rate_tree = rate_tree[0]
        rate_four = list(map(lambda x: x['rate_four'] , rates))
        rate_four = rate_four[0]
        sims = list(map(lambda x: x['sims_alg'] , rates))
        sims = sims[0]
    except:
        notFound = True
        rate_actual = 0.0
        numVotos = 0.0
        rate_one = 0
        rate_two = 0
        rate_tree = 0
        rate_four = 0
        sims = 0.0
        rate_total = 0
        sims_total = 0
        rates_totals = 0

    #Get Data from all Documents
    try:
        if(notFound == False):
            total = db[collection_rating].find()
            total = [rate_total for rate_total in total]
            rate_total = list(map(lambda x: x['rate_average'] , total))
            sims_total = list(map(lambda x: x['sims_alg'] , total)) 
    except:
        print("banco nao tem acesso")


    #Trated the string values
    treated_rate = []
    if(notFound == False):
            for rate in rate_total:
                try:
                    rate = float(rate)      
                    treated_rate.append(rate)        
                except:
                    pass
            #Set totals values
            length = len(rate_total) #get size of array
            rates_totals = round(sum(treated_rate)/length,2)
            sims_total = round(sum(sims_total)/length,2)


    #Create pizza graph
    df2 = pd.DataFrame({
            "N° de votos": [rate_four, rate_tree, rate_two, rate_one],
            "Avaliação": ['Muito similares', 'Boa similaridade', 'Pouco Similares', 'Nenhuma Similaridade']     
    })
         
    fig2 = px.pie(df2, values="N° de votos", names="Avaliação")

    fig2.update_layout(
            height=550,
            width=550,
    )
    fig2.update_traces(marker_colors=colors_pizza)


    #Create bar graph
    df = pd.DataFrame({
        "Avaliação dos Usuários x Resultado Algoritmo": ["Usuário", "Algoritmo","Usuário", "Algoritmo"],
        "Notas médias": [rate_actual,sims, rates_totals,  sims_total],
        "Avaliação": ["Nota específica","Nota específica","Geral",  "Geral"]
    })

    fig = px.bar(df, x="Avaliação dos Usuários x Resultado Algoritmo", y="Notas médias",  color="Avaliação", barmode="group",
        color_discrete_sequence =["#1e175c", '#6357d4', "#1e175c", '#6357d4']
    )

    fig.update_layout(
        font_color=colors['text'],
        height=435,
        width=700,
    )



    if(link == None):
        showLink = 'Nenhuma notícia selecionada'
        alert = "alert alert-info"
    elif(numVotos == 0.0):
        showLink = 'Não há nenhuma avaliação para este link'
        alert = "alert alert-danger"
    else:
        showLink = "Notícia selecionada -> " + link
        alert = "alert alert-success"

    return html.Div([
        
        html.Div(className=alert, children='''
            {}.
        '''.format(showLink), 
            style={
                #'textAlign': 'center',
                'marginLeft':'50px',
                'marginRight':'50px',  
                'fontFamily': 'Verdana',
                'color': "#3b2cbf",
                'marginTop': '15px',
                'fontWeight': 'bold',
            }
        ),
        dcc.Graph(
            id='graph_bar',
            style={'float': 'left', 'display': 'flex', 'flex':1},
            figure=fig
        ),
        dcc.Graph(
            id='graph_pizza',
            style={'marginRight': 'auto', 'display': 'flex', 'flex':1,},
            figure=fig2
        ),
    ])

    

if __name__ == '__main__':
    app.run_server(debug=True)