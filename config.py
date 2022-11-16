PORT = '8050'
HOST = '0.0.0.0'
URL_SUBPATH = '/barometre-open-access-uca/'
PERIOD = [2016,2022]
PUBLIS_OBS_DATES = ["20220829","20210914","20201130"]
PUBLIS_LAST_OBS_DATE = "20220829"
THESES_OBS_DATE = ["20220530"]
THESES_LAST_OBS_DATE = "20220530"
PLOTLY_TEMPLATE = "simple_white"
COLORS = {'Accès fermé': 'rgb(38,40,63)',
          'Accès ouvert': 'rgb(255, 111, 76)',
          'Archive ouverte': 'rgb(25,144,91)',
          'Editeur': 'rgb(234,215,55)',
          'Editeur et archive ouverte':'rgb(145,174,79)',
          'Gold': 'rgb(255, 232, 0)',
          'Green': '#008941',
          'Hybrid': 'rgb(139, 118, 87)',
          'Bronze': 'rgb(255, 136, 101)',
          'Sciences, Technologies, Santé': 'rgb(56, 166, 165)',
          'Lettres, sciences Humaines et Sociales': 'rgb(237, 173, 8)'}
LINE_DASH_MAP = {'2022': 'solid', '2021': 'dot', '2020': 'dash'}