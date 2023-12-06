from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

api_base = "https://modd-anime-api.onrender.com"

def get_data(api_url):
    api_key = os.environ.get('API_KEY')  
    if not api_key:
        print("API key not found in environment variables.")
        return None
    headers = {'X-API-Key': api_key}
    try:
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search',methods=["GET"])
def search():
    q =  request.args.get('q',default=None)
    page = int(request.args.get('page', 1))
    search_api_url = f"{api_base}/search?q={q}&page={page}"
    genre_api_url = f"{api_base}/genre"
    genre_data = get_data(genre_api_url)
    data = get_data(search_api_url)
    if data is not None:
        return render_template('cards.html', cards=data, page=page,q=q, genre=genre_data, def_route = "search.html")
    else:
        return "Error fetching data from the API"


@app.route('/recent',methods=["GET"])
def recent():
    page = int(request.args.get('page', 1))
    typ = int(request.args.get('typ', 1))
    genre_api_url = f"{api_base}/genre"
    genre_data = get_data(genre_api_url)
    recent_api_url = f"{api_base}/recent_release?type={typ}&page={page}"
    recent_data = get_data(recent_api_url)
    if recent_data is not None:
        return render_template('recent.html', cards=recent_data, page=page, typ=typ, genre=genre_data)
    else:
        return "Error Fetching data from the API"


@app.route('/route/<path:def_route>', methods=['GET'])
def default(def_route):
    page = int(request.args.get('page', 1))
    genre_api_url = f"{api_base}/genre"
    genre_data = get_data(genre_api_url)
    aph_param = request.args.get('aph', '')
    if def_route == 'anime-movies.html':
        def_api_url = f"{api_base}/route/{def_route}?aph={aph_param}&page={page}"
    else:
        def_api_url = f"{api_base}/route/{def_route}?page={page}"
    def_data = get_data(def_api_url)
    if def_data is not None:
        if def_route == 'anime-movies.html':
            movie_aph_list = get_data(f"{api_base}/movies")
            return render_template('cards.html', def_route = def_route,cards=def_data, page=page, genre=genre_data, aph=aph_param, movie_aph_list = movie_aph_list)
        else:
            return render_template('cards.html', def_route = def_route,cards=def_data, page=page, genre=genre_data)
    else:
        return "Error Fetching data from the API"

@app.route('/anime/<list_route>', methods=["GET"])
def anime_list(list_route):
    page = int(request.args.get('page', 1))
    genre_data = get_data(f"{api_base}/genre")
    anime_list = get_data(f"{api_base}/anime")
    ani_list_data = get_data(f"{api_base}/anime/{list_route}?page={page}")
    if ani_list_data is not None:
        return render_template("anime_list.html", ani_list_data = ani_list_data, genre = genre_data, page=page, anime_list = anime_list)
    else:
        return "Error Fetching data from the API"

@app.route('/anime/info/<path:slug>',methods=["GET"])
def anime_info(slug):
    genre_data = get_data(f"{api_base}/genre")
    anime_info = get_data(f"{api_base}/anime/info/{slug}")
    if anime_info is not None:
        return render_template("anime_info.html",anime_info=anime_info,genre=genre_data)
    else:
        return "Error Fetching data from the API"

@app.route('/episode_list', methods=['GET'])
def episode_list():
    ep_start = int(request.args.get('ep_start', 1))
    ep_end = int(request.args.get('ep_end', 10))
    movie_id = request.args.get('movie_id')
    default_ep = request.args.get('default_ep')
    alias_anime = request.args.get('alias_anime')
    episode_lists = get_data(f"{api_base}/anime/episodes?ep_start={ep_start}&ep_end={ep_end}&movie_id={movie_id}&default_ep={default_ep}&alias_anime={alias_anime}")
    if episode_lists is not None:
        return render_template(
            'episode_list.html', episode_lists=episode_lists,
            ep_start=ep_start,
        ep_end=ep_end,
        movie_id=movie_id,
        default_ep=default_ep,
        alias_anime=alias_anime,)
    else:
        return "Error Fetching data from the API"


@app.route('/play/<path:slug>',methods=["GET"])
def play(slug):
    data = get_data(f"{api_base}/{slug}")
    download_links = [data['download']]
    stream_links = [link for server in data['streams'] for link in server['vidcdn']]
    play_data = {'download_links': download_links, 'stream_links': stream_links}
    ep_start = int(request.args.get('ep_start', 1))
    ep_end = int(request.args.get('ep_end', 10))
    movie_id = request.args.get('movie_id')
    default_ep = request.args.get('default_ep')
    alias_anime = request.args.get('alias_anime')
    episode_lists = get_data(f"{api_base}/anime/episodes?ep_start={ep_start}&ep_end={ep_end}&movie_id={movie_id}&default_ep={default_ep}&alias_anime={alias_anime}")
    if play_data is not None:
    # Pass all the arguments to the template
        return render_template(
        'play.html',
        play_data=play_data,
        episode_lists=episode_lists,
        ep_start=ep_start,
        ep_end=ep_end,
        movie_id=movie_id,
        default_ep=default_ep,
        alias_anime=alias_anime,
    )
    else:
        return "Error Fetching data from the API"

if __name__ == '__main__':
    app.run(debug=True)
