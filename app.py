import streamlit as st
import pickle
from PIL import Image
import requests
from math import ceil
import base64
from io import BytesIO
import bz2
import pickle
import _pickle as cPickle

im = Image.open("favicon.png")
st.set_page_config(
    page_title="Recommender System",
    page_icon=im,
    layout='wide'
)


def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = cPickle.load(data)
    return data

@st.cache(suppress_st_warning=False)
def s3():
    return decompress_pickle('similarity3.pbz2')
similarity3 = s3()

# DO NOT CHANGE LINE 7-14
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
.stApp {
  background-image: url("data:image/png;base64,%s");
  background-size: cover;
}
</style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background('src/static/img.png')

st.markdown("<h1 style='text-align: center; color: red;'>Movie Recommender System</h1>", unsafe_allow_html=True)


# main recommendation part
def recommend_movies(movie):
    temp = str(movie)
    temp = temp.split()
    if len(temp) > 1:
        if temp[0] in ['A', 'An', 'The'] and len(temp) == 2:
            temp = temp[1]
        elif len(temp) > 2 and temp[0] not in ['A', 'An', 'The']:
            temp = ' '.join(temp[:2])
        else:
            temp = ' '.join(temp)
    else:
        temp = temp[0]

    recommended_list = []
    photo_list = []
    for index, row in all_movies.iterrows():
        # print(row)
        curr = row[0]
        id = int(row.movie_id)
        # st.text(id)
        if temp in curr and movie != curr:
            recommended_list.append(curr)
            photo_list.append(fetch_poster(id))
            # print(curr)

    # calculate the index of the movie
    index = all_movies[all_movies['Title'] == movie].index[0]

    # print("\n based on cast -----------------------------------")
    # distances
    dist2 = similarity2[index]
    distances = sorted(list(enumerate(dist2)), reverse=True, key=lambda x: x[1])
    for i in distances[0:6]:
        curr = all_movies.iloc[i[0]].Title
        id = all_movies[all_movies['Title'] == curr]['movie_id'].values[0]
        if curr != movie:
            # print(curr)
            if curr not in recommended_list:
                recommended_list.append(curr)
                photo_list.append(fetch_poster(id))

    # print("\n based on tag ---------------------------------")

    dist1 = similarity1[index]
    distances = sorted(list(enumerate(dist1)), reverse=True, key=lambda x: x[1])
    for i in distances[0:6]:
        curr = all_movies.iloc[i[0]].Title
        id = all_movies[all_movies['Title'] == curr]['movie_id'].values[0]
        # st.text(id)
        if curr != movie:
            # print(curr)
            if curr not in recommended_list:
                recommended_list.append(curr)
                photo_list.append(fetch_poster(id))

        # print("\n based on director ---------------------------------")

        dist3 = similarity3[index]
        distances = sorted(list(enumerate(dist3)), reverse=True, key=lambda x: x[1])
        for i in distances[0:6]:
            curr = all_movies.iloc[i[0]].Title
            id = all_movies[all_movies['Title'] == curr]['movie_id'].values[0]
            if curr != movie:
                # print(curr)
                if curr not in recommended_list:
                    recommended_list.append(curr)
                    photo_list.append(fetch_poster(id))

    # print("\nbased on genre ---------------------------------")

    dist4 = similarity4[index]
    distances = sorted(list(enumerate(dist4)), reverse=True, key=lambda x: x[1])
    for i in distances[0:6]:
        curr = all_movies.iloc[i[0]].Title
        id = all_movies[all_movies['Title'] == curr]['movie_id'].values[0]
        if curr != movie:
            # print(curr)
            if curr not in recommended_list:
                recommended_list.append(curr)
                photo_list.append(fetch_poster(id))

    return [recommended_list, photo_list]


# collecting the movies list from ipynb file as pickle files
all_movies = pickle.load(open('movies.pkl', 'rb'))

@st.cache(suppress_st_warning=True)
def s4():
    return decompress_pickle('similarity4.pbz2')
similarity4 = s4()


def fetch_poster(id):
    api_key = '8cb85690b8c1dfe9317de8b51bafc493'
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(id, api_key))
    data = response.json()
    # st.text(data)
    # st.text(id)
    ext = data.get('poster_path', None)
    if ext is None:
        return "https://www.google.com/search?q=image+not+available&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiZhYfp9e32AhWfR2wGHXGMCQAQ_AUoAXoECAEQAw&biw=1366&bih=649&dpr=1#imgrc=QJnWwlLEbJmpBM"
    path = "https://image.tmdb.org/t/p/w500" + ext
    return path


def fetch_cast_poster(index, id):
    api_key = '8cb85690b8c1dfe9317de8b51bafc493'
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}/credits?api_key={}&language=en-US'.format(id, api_key))
    data = response.json()
    ext = data.get('cast')[index].get("profile_path", None)
    # st.text(data)
    if ext is None:
        return "https://www.google.com/search?q=image+not+available&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiZhYfp9e32AhWfR2wGHXGMCQAQ_AUoAXoECAEQAw&biw=1366&bih=649&dpr=1#imgrc=QJnWwlLEbJmpBM"
    path = "https://image.tmdb.org/t/p/w500" + ext
    return path


def fetch_cast(index, id):
    api_key = '8cb85690b8c1dfe9317de8b51bafc493'
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}/credits?api_key={}&language=en-US'.format(id, api_key))
    data = response.json()
    ext = data.get('cast')[index].get("name", None)
    # st.text(data)
    if ext is None:
        return "N/A"
    return ext


def resize_img(photo, x, y):
    r = requests.get(photo)
    img = Image.open(BytesIO(r.content))
    resizedImg = img.resize((x, y), Image.ANTIALIAS)
    return resizedImg


def get_movie_id(name):
    return all_movies[all_movies['Title'] == name]['movie_id'].values[0]


def get_tmdb_dict(id):
    api_key = '8cb85690b8c1dfe9317de8b51bafc493'
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(id, api_key))
    data = response.json()
    return data


def get_omdb_dict(imdb_id):
    omdb_link = "http://www.omdbapi.com/?i={}&apikey=c4177c63".format(imdb_id)
    omdb_dict = requests.get(omdb_link).json()
    return omdb_dict


# provides a button and check if it is clicked
with st.form(key='my_form'):
    # select the movie
    st.markdown("<h6 style='text-align: left; color: white;'>Which Movie Have You Recently Watched...</h6>",
                unsafe_allow_html=True)

    selected_movie = st.selectbox("", all_movies['Title'].values)
    submit_button = st.form_submit_button(label='Submit')
    if submit_button is True:

        with st.spinner('Loading...'):

            id = get_movie_id(selected_movie)
            data = get_tmdb_dict(id)

            cols = st.columns(2)
            with cols[0]:
                st.image(resize_img(fetch_poster(id), 450, 600))

                @st.cache(suppress_st_warning=True)
                def s2():
                    return decompress_pickle('similarity2.pbz2')
                similarity2 = s2()

            with cols[1]:
                st.markdown(f"<h2 style='text-align: left; color: yellow;'>{selected_movie}</h2>", unsafe_allow_html=True)
                st.write(
                    f"<h6 style='text-align: left; color: white;'>{data.get('overview')}</h6>",
                    unsafe_allow_html=True)
                st.write(
                    f"<h3 style='text-align: left; color: white;'>Year of Release: {data.get('release_date').split('-')[0]}</h3>",
                    unsafe_allow_html=True)

                imdb_id = data.get('imdb_id')
                omdb_dict = get_omdb_dict(imdb_id)

                ratings = omdb_dict.get('Ratings')
                director = omdb_dict.get('Director')
                genre = omdb_dict.get('Genre')
                Runtime = omdb_dict.get('Runtime')

                st.markdown(f"<h5 style='text-align: left; color: white;'>Directed by: {director}</h5>",
                            unsafe_allow_html=True)
                st.markdown(f"<h5 style='text-align: left; color: white;'>Genre: {genre}</h5>", unsafe_allow_html=True)
                for _ in range(len(ratings)):
                    source = ratings[_].get("Source")
                    rating = ratings[_].get("Value")
                    if source == "Internet Movie Database":
                        source = "IMDB"
                    if not source or not rating:
                        continue
                    st.markdown(f"<h5 style='text-align: left; color: white;'>{source}: {rating}</h5>",
                                unsafe_allow_html=True)
                st.markdown(f"<h5 style='text-align: left; color: white;'>Runtime: {Runtime}</h5>", unsafe_allow_html=True)


            @st.cache(suppress_st_warning=True)
            def s1():
                return decompress_pickle('similarity1.pbz2')
            similarity1 = s1()

            count = 0
            cast_photo_list = []
            cast_list = []
            while True:

                # st.text(id)
                if count == 5:
                    break
                try:
                    cast_photo_list.append(fetch_cast_poster(count, id))
                    cast_list.append(fetch_cast(count, id))
                    count += 1
                except:
                    break
            with st.spinner('Loading...'):
                st.header("Top Cast")

                columns = st.columns(5)
                recommended = recommend_movies(selected_movie)

                for i in range(5):
                    with columns[i]:
                        try:
                            st.write(cast_list[i])
                            st.image(cast_photo_list[i])
                        except:
                            break

                st.header("You Can Also Watch...")
                with st.spinner('Loading...'):
                    # columns = st.columns(5)
                    from itertools import cycle

                    filteredImages = recommended[1]  # your images here
                    caption = recommended[0]  # your caption here
                    cols = st.columns(4)

                    for iteration in range(len(recommended[0])):
                        name, photo = caption[iteration], filteredImages[iteration]
                        with cols[iteration % 4]:
                            st.write(name)
                            st.image(resize_img(photo, 300, 400))

                            with st.expander(label=str("See Details"), expanded=False):
                                id = get_movie_id(name)
                                data = get_tmdb_dict(id)
                                imdb_id = data.get('imdb_id')
                                omdb_dict = get_omdb_dict(imdb_id)

                                st.write(f"**{omdb_dict.get('Title')}**")
                                st.write("**Directed by:** " + omdb_dict.get("Director"))
                                st.write("**Overview:** " + omdb_dict.get("Plot"))
                                st.write(f'**{omdb_dict.get("Year")}**')
                                st.write(f'**IMDB: {omdb_dict.get("imdbRating")}/10**')
