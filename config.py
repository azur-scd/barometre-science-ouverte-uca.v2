PORT = '8050'
HOST = '0.0.0.0'
URL_SUBPATH = '/barometre-science-ouverte-uca/'
PUBLIS_PERIOD = [2016,2022]
PUBLIS_OBS_DATES = ["20220829","20210914","20201130"]
PUBLIS_LAST_OBS_DATE = "20220829"
THESES_OBS_DATES = ["20221017","20220530"]
THESES_LAST_OBS_DATE = "20221017"
THESES_PERIOD = [2013,2022]
PLOTLY_TEMPLATE = "simple_white"
COLORS = {'Accès fermé': 'rgb(38,40,63)', #publis
          'Accès ouvert': 'rgb(255, 111, 76)', #publis
          'Archive ouverte': 'rgb(25,144,91)', #publis
          'Editeur': 'rgb(234,215,55)', #publis
          'Editeur et archive ouverte':'rgb(145,174,79)', #publis
          'Gold': 'rgb(255, 232, 0)', #publis
          'Green': '#008941', #publis
          'Hybrid': 'rgb(139, 118, 87)', #publis
          'Bronze': 'rgb(255, 136, 101)', #publis
          'Sciences, Technologies, Santé': 'rgb(56, 166, 165)',
          'Lettres, sciences Humaines et Sociales': 'rgb(237, 173, 8)',
          'Accès restreint': 'rgb(38,40,63)', # theses
          'Accès libre': 'rgb(86, 215, 136)', #theses
          }
LINE_DASH_MAP = {'2022': 'solid', '2021': 'dot', '2020': 'dash'}