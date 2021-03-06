from articles_app.models import Observations, Articles, Stocks
from NLGengine.analyse import Analyse
from NLGengine.observation import Observation
from NLGengine.paragraph import Paragraph
from NLGengine.article import Article
from NLGengine.content_determination.nndeterminator import NNDeterminator, load_model
from NLGengine.content_determination.nnmatrix_trainer import NNMatrixTrainer
from NLGengine.content_determination.rules import Rules
from NLGengine.microplanning.planner import Planner
from NLGengine.realisation.realiser import Realiser

import articles_app.image_transform as imgtr
import articles_app.utils as util
import pandas as pd
import numpy as np

import os
import json
import itertools
from datetime import datetime, timedelta
import cv2
import uuid


# defining some statics
AI_VERSION = 1.6


def select_observations(initial_obs, observation_set: list, sector_focus: list, art_type: str, max_reps: int = 3,
                        max_obs: int = 5, par_amount: int = 3):
    """Selects all the observations for the paragraphs.

    Args:
        initial_obs (NLGengine.observation.Observation): The initial chosen observation
        observation_set (list): A list with all the observations to choose from
        sector_focus (list): A list with the sectors to focus on
        art_type (str): The type of the chosen article
        max_reps (int, optional): The maximal amount of repetitions of the same component in the same paragraph. Defaults to 3.
        max_obs (int, optional): The maximal amount of observations in a paragraph. Defaults to 5.
        par_amount (int, optional): The amount of paragraphs in an article. Defaults to 3.

    Returns:
        list: A list with all the paragraphs in the text
    """

    # set the initial observation
    chosen_observs = [initial_obs]
    # set a list to save all paragraphs
    all_pars = []
    # load in the model
    model = load_model()

    # loop over the amount of paragraphs needed
    for _ in range(par_amount):
        # set a list to save the observation for this paragraph
        par = []
        # indicate that a new paragraph is started
        new_par = True

        # loop over the max amount of observations in a paragraph
        for _ in range(max_obs):

            determinator = NNDeterminator(model, observation_set, chosen_observs, sector_focus, art_type)
            determinator.calculate_new_situational_relevance(new_par)
            # reset the new_par
            new_par = False

            # get the newly chosen observation
            new_observ = determinator.get_highest_relevance()
            # save the chosen observation into the history and the paragraph
            chosen_observs.append(new_observ)
            par.append(new_observ)
            # reset all observations
            observation_set = determinator.all_observations

            # check whether no rules are broken (more than 3 mentions of the same component in one paragraph)
            if Rules.x_times_repeat_comp(max_reps, par):
                # more than 3 mentions of the same component in one paragraph
                break

        # save the current paragraph in its class
        _par = Paragraph(par)
        all_pars.append(_par)

    # return all the paragraphs
    return all_pars


def build_article(user_name, filters, bot=False):
    """Build an article based on the most recent and relevant observations.

    Args:
        user_name (String): The name of the user that is generating the article
        filters (dict): The filters that has been chosen for the selection of the Observations

    Returns:
        int: The id of the generated article
    """
    # check if filters on period are activated
    periods = filters.get("Periode")
    # get the max and min range of the period
    min_date, max_date = util.get_period_range(periods.get("options"))

    # get the type of the article
    art_type = filters.get("Type").get("options")

    # retrieve the sectors to focus on
    sector_focus = filters.get("Sector").get("options")

    # retrieve all relevant observations from the Observations table
    observation_set = list(Observations.objects.filter(period_end__lte=max_date)
                                               .order_by('-period_end', '-relevance'))[:1000]

    # get the initial observation
    first = observation_set.pop(0)
    first_observ = Observation(first.serie,
                               first.period_begin,
                               first.period_end,
                               first.pattern,
                               first.sector,
                               first.indexx,
                               first.perc_change,
                               first.abs_change,
                               first.observation,
                               float(first.relevance),
                               first.meta_data,
                               oid=first.id)

    # setup before the beginning of the generation
    observation_set = [Observation(x.serie,
                                   x.period_begin,
                                   x.period_end,
                                   x.pattern,
                                   x.sector,
                                   x.indexx,
                                   x.perc_change,
                                   x.abs_change,
                                   x.observation,
                                   float(x.relevance),
                                   x.meta_data,
                                   oid=x.id) for x in observation_set]

    # get the filters for amount of paragraphs and sentences
    am_par = int(filters.get("Paragrafen").get("options"))
    am_sen = int(filters.get("Zinnen").get("options"))

    # select all the observations / paragraphs
    paragraphs = select_observations(first_observ, observation_set, sector_focus, art_type, max_obs=am_sen, par_amount=am_par)

    # set the chosen observations /paragrahps to the planner
    planner = Planner(paragraphs)
    planner.plan()

    # set the planned observations /paragraphs into the realiser
    realiser = Realiser(planner.paragraphs)
    realiser.realise()

    # build the article
    art = Article(realiser.paragraphs)
    art.build()

    # get the meta data and save it into the article
    meta = {}
    meta["manual"] = filters.get("manual")
    meta["filters"] = {}
    meta["observs"] = art.observs_id
    meta["sit_relev"] = art.sit_relev

    for x in ["Sector", "Periode"]:
        selection = filters.get(x)
        if (selection.get("total") != len(selection.get("options"))) and (selection.get("options") != []):
            meta["filters"][x] = selection.get("options")
        else:
            meta["filters"][x] = "Alles"

    # get all chosen observations
    all_observations = list(itertools.chain.from_iterable([x.observations for x in realiser.paragraphs]))

    # select the focus of the image
    comps_focus = []
    sector_focus = []
    for observ in all_observations:
        if observ.meta_data.get("components"):
            comps_focus.extend(observ.meta_data.get("components"))
        else:
            comps_focus.append(observ.serie)

        if observ.meta_data.get("sectors"):
            sector_focus.extend(observ.meta_data.get("sectors"))
        else:
            sector_focus.append(observ.sector)

    # delete the AMX and duplicates
    comps_focus = [x for x in comps_focus if x != "AMX"]
    comps_focus = list(dict.fromkeys(comps_focus))
    sector_focus = sector_focus[0]

    # build a image for the article
    img_array = generate_article_photo(comps_focus, sector_focus)
    file_name = f"{uuid.uuid1().hex}.jpg"
    save_url = f"./media/images/{file_name}"
    retrieve_url = f"images/{file_name}"
    cv2.imwrite(save_url, img_array)

    article = Articles()
    article.title = generate_article_title(art_type, periods.get("options"), max_date)
    article.top_image = retrieve_url
    article.content = art.content
    article.date = datetime.now()
    article.AI_version = AI_VERSION
    article.meta_data = meta
    if bot:
        article.author = "nieuwsbot"
    else:
        article.author = user_name
    article.save()

    return article.id


def generate_article_title(art_type: str, period: str, begin_date):
    """Generates the title of the article based on the article type and period.

    Args:
        art_type (str): The type of the article
        period (str): The period from the filter
        begin_date (datetime.datetime): The begin date of the article

    Returns:
        str: Returns the build title string
    """
    if art_type == "dagartikel":
        # build the title for the article type 'dagartikel'
        title = f"Beurs update {begin_date.strftime('%d %b')}"

    elif art_type == "weekartikel":
        # build the title for the article type 'weekartikel'
        title = f"Beurs weekoverzicht week {begin_date.isocalendar()[1]}"

    elif art_type == "maandartikel":
        # build the title for the article type 'maandartikel'
        title = f"Beurs maandoverzicht {period}"

    return title


def construct_article(user_name, content, filters, title):
    """Build an article based on a sentence construction the user has made.

    Args:
        user_name (String): The name of the user that is generating the article
        content (list): The array with all the chosen observations by the user
        filters (dict): The filters that has been chosen for the selection of the Observations
        title (String): The title of the article

    Returns:
        int: The id of the newly generated article
    """
    # get all the chosen observations, set the situational relevance to the normal relevance
    # and select all sentences of the to be article
    observation_set = []
    sit_relev = []
    observs_id = []
    sentences = []
    for row in content:
        # get the observation from the database
        observ = Observations.objects.get(id=row[0])
        # save the observation, id and text into the coresponding array
        observation_set.append(observ)
        sit_relev.append(float(observ.relevance))
        observs_id.append(observ.id)
        sentences.append(observ.observation)

    # build the article by appending all observations
    content = " ".join(sentences)

    # get the meta data and save it into the article
    meta = {}
    meta["manual"] = filters.get("manual")
    meta["filters"] = {}
    meta["observs"] = observs_id
    meta["sit_relev"] = sit_relev

    for x in ["Sector", "Periode"]:
        selection = filters.get(x)
        if (selection.get("total") != len(selection.get("options"))) and (selection.get("options") != []):
            meta["filters"][x] = selection.get("options")
        else:
            meta["filters"][x] = "Alles"

    # select the focus of the image
    comps_focus = []
    sector_focus = []
    for observ in observation_set[:3]:
        if observ.meta_data.get("components"):
            comps_focus.extend(observ.meta_data.get("components"))
        else:
            comps_focus.append(observ.serie)

        if observ.meta_data.get("sectors"):
            sector_focus.extend(observ.meta_data.get("sectors"))
        else:
            sector_focus.append(observ.sector)

    # delete the AMX and duplicates
    comps_focus = [x for x in comps_focus if x != "AMX"]
    comps_focus = list(dict.fromkeys(comps_focus))
    sector_focus = sector_focus[0]

    # build an image for the article
    img_array = generate_article_photo(comps_focus, sector_focus)
    file_name = f"{uuid.uuid1().hex}.jpg"
    save_url = f"./media/images/{file_name}"
    retrieve_url = f"images/{file_name}"
    cv2.imwrite(save_url, img_array)

    article = Articles()
    # TODO get the max date
    if title == "":
        article.title = f"Beurs update {datetime.now().strftime('%d %b')}"
    else:
        article.title = title

    article.top_image = retrieve_url
    article.content = content
    article.date = datetime.now()
    article.AI_version = AI_VERSION
    article.meta_data = meta
    article.author = user_name
    article.save()

    return article.id


def get_test_case_info():
    """Retrieve all the test cases with the corresponding scores.

    Returns:
        dict: Returns a dictionary with the scores on the test set
    """
    m = NNMatrixTrainer()
    return m.get_evaluations()


def generate_and_save_headline_img(comp_focus: list, sector_focus: str = None, verbose: bool = False, showImage: bool = True):
    """Generates a photo based on the components and saves it.

    Args:
        comp_focus (list): A list of the components that have to be in the photo of the article (max 2)
        sector_focus (str, optional): The sector where the article is focussing on. Defaults to None
        verbose (bool, optional): Prints the file name of the saved image. Defaults to False
        show_image (bool, optional): Decides whether to show the image in a new window after generation. Defaults to True
    """
    img_array = generate_article_photo(comp_focus, sector_focus)
    file_name = f"{uuid.uuid1().hex}.jpg"
    save_url = f"./media/images/{file_name}"
    retrieve_url = f"images/{file_name}"
    cv2.imwrite(save_url, img_array)

    if verbose:
        print(f"file_name:{file_name}")

    if showImage:
        cv2.imshow('dst', img_array)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()


# TODO format this function!!
def generate_article_photo(components: list, sector_focus: str = None):
    """Generates the a photo for a specific article.

    Args:
        components (list): A list of the components that have to be in the photo of the article (max 2)
        sector_focus (str, optional): The sector where the article is focussing on. Defaults to None.

    Returns:
        np.array: The generated picture
    """
    sector_dir = r"./articles_app/data/article_backgrounds/sector"
    generic_dir = r"./articles_app/data/article_backgrounds/generic"
    logos_dir = r"./articles_app/data/companylogos"

    # select the background picture
    if sector_focus and os.path.isfile(f"{sector_dir}/{sector_focus}_background.jpg"):
        # there is a focus on a sector and a background picture exists for that sector
        background = cv2.imread(f"{sector_dir}/{sector_focus}_background.jpg")
    else:
        # there is no focus on a sector or the sector does not exists, therefore a random picture is chosen
        rdm_background = np.random.choice(os.listdir(generic_dir))
        background = cv2.imread(f"{generic_dir}/{rdm_background}")

    # resize the background to the good size
    # resize dimensions in (width, height)
    background = cv2.resize(background, (700, 422), interpolation=cv2.INTER_AREA)

    # read in the images of the components
    if len(components) == 1:
        # only one component in the picture
        comps = (cv2.imread(f"{logos_dir}/{components[0]}.png", cv2.IMREAD_UNCHANGED),)
    elif len(components) == 2:
        # two components in the picture
        comps = (cv2.imread(f"{logos_dir}/{components[0]}.png",
                 cv2.IMREAD_UNCHANGED),
                 cv2.imread(f"{logos_dir}/{components[1]}.png",
                 cv2.IMREAD_UNCHANGED))
    else:
        # more than two (pic the first 2)
        comps = (cv2.imread(f"{logos_dir}/{components[0]}.png",
                 cv2.IMREAD_UNCHANGED),
                 cv2.imread(f"{logos_dir}/{components[1]}.png",
                 cv2.IMREAD_UNCHANGED))

    # check how many components there are
    if len(comps) == 1:
        # only one component to be showcased
        # numpy shape returns (H, W, D)
        img = comps[0]

        # check for shape, if it is more rectangular or cubic
        if img.shape[1] > 2 * img.shape[0]:
            # width is far wider than the height
            img = imgtr.resize_image(img, 450)
        else:
            # width is allmost equal to height
            img = imgtr.resize_image(img, 350)

        # adding image into the middle of the background
        x_pos = int((background.shape[1] / 2) - (img.shape[1] / 2))
        y_pos = int((background.shape[0] / 2) - (img.shape[0] / 2))
        new_image = imgtr.overlay_transparent(background, img, x_pos, y_pos)

    else:
        # two components to be showcased
        img1 = comps[0]
        img2 = comps[1]

        # check for shapes of the images, if they are both more rectangular or cubic
        if (img1.shape[1] > 2 * img1.shape[0]) and (img2.shape[1] > 2 * img2.shape[0]):
            print("both rectangular")
            # both widths are far wider than the height
            img1 = imgtr.resize_image(img1, 300)
            img2 = imgtr.resize_image(img2, 300)

            # calculate the positions of the images
            x_pos1 = int((background.shape[1] / 2) - (img1.shape[1] / 2))
            y_pos1 = int((background.shape[0] / 3) * 1 - (img1.shape[0] / 2))
            x_pos2 = int((background.shape[1] / 2) - (img2.shape[1] / 2))
            y_pos2 = int((background.shape[0] / 3) * 2 - (img2.shape[0] / 2))

            # add the new images
            new_image = imgtr.overlay_transparent(background, img1, x_pos1, y_pos1)
            new_image = imgtr.overlay_transparent(new_image, img2, x_pos2, y_pos2)

        elif (img1.shape[1] > 2 * img1.shape[0]):
            print("first more rectangular")
            # width of first image far wider than the height
            img1 = imgtr.resize_image(img1, 280)
            img2 = imgtr.resize_image(img2, 280)

            # calculate the positions of the images
            x_pos1 = int((background.shape[1] / 2) - (img1.shape[1] / 2))
            y_pos1 = int((background.shape[0] / 3) * 1 - (img1.shape[0] / 2))
            x_pos2 = int((background.shape[1] / 2) - (img2.shape[1] / 2))
            y_pos2 = int((background.shape[0] / 3) * 2 - (img2.shape[0] / 2))

            # add the new images
            new_image = imgtr.overlay_transparent(background, img1, x_pos1, y_pos1)
            new_image = imgtr.overlay_transparent(new_image, img2, x_pos2, y_pos2)

        elif (img2.shape[1] > 2 * img2.shape[0]):
            print("second more rectangular")
            # width of second image far wider than the height
            img1 = imgtr.resize_image(img1, 270)
            img2 = imgtr.resize_image(img2, 270)

            # calculate the positions of the images
            x_pos1 = int((background.shape[1] / 2) - (img1.shape[1] / 2))
            y_pos1 = int((background.shape[0] / 3) * 1 - (img1.shape[0] / 2))
            x_pos2 = int((background.shape[1] / 2) - (img2.shape[1] / 2))
            y_pos2 = int((background.shape[0] / 3) * 2 - (img2.shape[0] / 2))
            # add the new images
            new_image = imgtr.overlay_transparent(background, img1, x_pos1, y_pos1)
            new_image = imgtr.overlay_transparent(new_image, img2, x_pos2, y_pos2)

        else:
            print("no-one more rectangular")
            # no width far wider than the height
            img1 = imgtr.resize_image(img1, 270)
            img2 = imgtr.resize_image(img2, 270)

            # calculate the positions of the images
            x_pos1 = int((background.shape[1] / 4) * 1 - (img1.shape[1] / 2))
            y_pos1 = int((background.shape[0] / 2) - (img1.shape[0] / 2))
            x_pos2 = int((background.shape[1] / 4) * 3 - (img2.shape[1] / 2))
            y_pos2 = int((background.shape[0] / 2) - (img2.shape[0] / 2))

            # add the new images
            new_image = imgtr.overlay_transparent(background, img1, x_pos1, y_pos1)
            new_image = imgtr.overlay_transparent(new_image, img2, x_pos2, y_pos2)

    return new_image


def find_new_observations(period_begin: datetime, period_end: datetime, to_db=False, to_prompt=False, to_list=False):
    """Runs all functions to find observations, collects the observations and deals with them in the proper way.

    Args:
        to_db (bool, optional): Decide whether the new observations are to be written into the database. Defaults to False.
        to_prompt (bool, optional): Decide whether the new observations are to be written to the prompt. Defaults to False.
        to_list (bool, optional): Decide whether the new observations are to be returned as a list of observations. Defaults to False.
    """
    all_observations = []

    all_observations.extend(run_period_observations(period_begin, period_end))
    all_observations.extend(run_week_observations(period_begin, period_end))
    all_observations.extend(run_trend_observations(period_end, 14))

    if to_db:
        # write all the found observations into the database
        for observ in all_observations:
            observation_to_database(observ.serie,
                                    observ.period_begin,
                                    observ.period_end,
                                    observ.pattern,
                                    observ.sector,
                                    observ.indexx,
                                    observ.observation,
                                    observ.perc_change,
                                    observ.abs_change,
                                    observ.relevance1,
                                    observ.meta_data)

    if to_prompt:
        # write all the found observations to the prompt
        for observ in all_observations:
            print(observ)
            print(observ.period_begin, observ.period_end)

    if to_list:
        # return the list of observations
        return all_observations


def run_period_observations(period_begin, period_end):
    """
    Get all the relevant data in the period and run the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period

    Returns:
        list: A list with the observations found
    """
    observs = []

    # retrieve all data over the stocks in this period
    data = Stocks.objects.filter(date__range=(period_begin, period_end))
    if len(data) > 0:
        # there is available stock data

        # convert the data to a dataframe
        q = data.values('component', 'indexx', 'date', 's_close')
        df_data = pd.DataFrame.from_records(q)

        # prepare the data for the analysis
        df_data.rename(columns={"s_close": "close"}, inplace=True)
        df_data['close'] = df_data['close'].astype('float')

        # load in the sector data and add it to the dataframe
        with open(r"./articles_app/data/sectorcompany.json") as f:
            sector_info = json.load(f)
        df_data["sector"] = df_data["component"].apply(lambda x: sector_info.get(x))
        df_data.dropna(inplace=True)

        # run the analyser to find observations
        analyse = Analyse(df_data, period_begin, period_end)
        analyse.find_period_observations()
        observs.extend(analyse.observations)

    return observs


def run_week_observations(period_begin, period_end):
    """
    Gets all the weeks in the range of the beginning and the end of the period and runs the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period

    Returns:
        list: A list with the observations found
    """
    observs = []
    # get all dates in the period range and find all unique weeknumbers
    all_dates = list(pd.date_range(period_begin, period_end))
    weeknumbers = list(set([x.isocalendar()[:2] for x in all_dates]))

    # get all the begin and end dates of the observable week (so the date of the monday and friday)
    # https://stackoverflow.com/questions/17087314/get-date-from-week-number
    all_periods = []
    for numb in weeknumbers:
        mon_date = datetime.strptime(f"{numb[0]}-W{numb[1]}" + '-1', '%G-W%V-%u')
        fri_date = mon_date + timedelta(4)
        all_periods.append((mon_date, fri_date))

    # run a new observation if the week hasn't been observerd
    if len(all_periods) > 0:
        for period in all_periods:
            # retrieve all data over the stocks in this period
            data = Stocks.objects.filter(date__range=period)
            if len(data) > 0:
                # convert the data to a dataframe
                q = data.values('component', 'indexx', 'date', 's_close')
                df_data = pd.DataFrame.from_records(q)

                # prepare the data for the analysis
                df_data.rename(columns={"s_close": "close"}, inplace=True)
                df_data['close'] = df_data['close'].astype('float')

                # load in the sector data and add it to the dataframe
                with open(r"./articles_app/data/sectorcompany.json") as f:
                    sector_info = json.load(f)
                df_data["sector"] = df_data["component"].apply(lambda x: sector_info.get(x))
                df_data.dropna(inplace=True)

                # run the analyser to find observations
                analyse = Analyse(df_data, *period)
                analyse.find_weekly_observations()
                observs.extend(analyse.observations)
    return observs


def run_trend_observations(period_end, delta_days):
    """Gets all the data between the beginning of the period and the end of the period and runs a trend analysis.

    Args:
        period_end (datetime): The date with the end of the period
        delta_days (int): Indicates how far back the data has to be retrieved

    Returns:
        list: A list with the observations found
    """
    observs = []
    # get the data for the trend analyses
    end_date = period_end
    begin_date = period_end - timedelta(delta_days)

    # retrieve all data over the stocks in this period
    data = Stocks.objects.filter(date__range=(begin_date, end_date))
    if len(data) > 0:
        # convert the data to a dataframe
        q = data.values('component', 'indexx', 'date', 's_close')
        df_data = pd.DataFrame.from_records(q)

        # prepare the data for the analysis
        df_data.rename(columns={"s_close": "close"}, inplace=True)
        df_data['close'] = df_data['close'].astype('float')

        # load in the sector data and add it to the dataframe
        with open(r"./articles_app/data/sectorcompany.json") as f:
            sector_info = json.load(f)
        df_data["sector"] = df_data["component"].apply(lambda x: sector_info.get(x))
        df_data.dropna(inplace=True)

        # run the analyser to find observations
        analyse = Analyse(df_data, begin_date, end_date)
        analyse.find_trend_observations()

        observs.extend(analyse.observations)
    return observs


def observation_to_database(serie, period_begin, period_end, pattern, sector, indexx, observation, perc, oabs, relevance, meta):
    """Writes an observation to the database.

    Args:
        serie (String): The name of the serie over which an observation has been made
        period_begin (datetime): The date with the beginning of the period of the observation
        period_end (datetime): The date with the end of the period of the observation
        pattern (String): A string with the pattern that was found
        sector (String): A string with the sector
        indexx (String): A string with the index of the component
        observation (String): A string with the sentence of the observation
        perc (float): A float with the percentage change
        oabs (float): A float with the absolute change
        relevance (Float): The relevance the observation holds
    """
    try:
        observ = Observations()
        observ.serie = serie
        observ.period_begin = period_begin
        observ.period_end = period_end
        observ.pattern = pattern
        observ.sector = sector
        observ.indexx = indexx
        observ.observation = observation
        observ.perc_change = round(perc, 2) if perc is not None else None
        observ.abs_change = oabs
        observ.relevance = relevance
        observ.meta_data = meta
        # save to the db
        observ.save()
    except Exception as e:
        print(f"{e}\n{observation}\n{meta}\n")


def update_observation(db_observ, norm_observ):
    """updates the values of an observation in the database based on the given Observation object.

    Args:
        db_observ (articles_app.models.Observations): The observation from the database
        norm_observ (NLGengine.observation.Observation): The observation with the updated data
    """
    try:
        db_observ.serie = norm_observ.serie
        db_observ.period_begin = norm_observ.period_begin
        db_observ.period_end = norm_observ.period_end
        db_observ.pattern = norm_observ.pattern
        db_observ.sector = norm_observ.sector
        db_observ.indexx = norm_observ.indexx
        db_observ.observation = norm_observ.observation
        db_observ.perc_change = round(norm_observ.perc_change, 2) if norm_observ.perc_change is not None else None
        db_observ.abs_change = norm_observ.abs_change
        db_observ.relevance = norm_observ.relevance1
        db_observ.meta_data = norm_observ.meta_data
        # update in the db
        db_observ.save()
    except Exception as e:
        print(f"{e}\n{norm_observ.observation}\n")
