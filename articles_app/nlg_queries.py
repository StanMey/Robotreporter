from articles_app.models import Observations, Articles, Stocks
from NLGengine.analyse import Analyse
from NLGengine.observation import Observation
from NLGengine.content_determination.determinator import Determinator
from NLGengine.microplanning.planner import Planner
from NLGengine.realisation.realiser import Realiser

import articles_app.image_transform as imgtr
import articles_app.utils as util
import pandas as pd
import numpy as np

import os
import json
from datetime import datetime, timedelta
import cv2
import uuid


# defining some statics
AI_VERSION = 1.5


def build_article(user_name, filters, bot=False):
    """Build an article based on the most recent and relevant observations.

    Args:
        user_name (String): The name of the user that is generating the article
        filters (dict): The filters that has been chosen for the selection of the Observations

    Returns:
        int: The id of the generated article
    """
    current_date = datetime.now().replace(hour=00, minute=00, second=00, microsecond=0)
    # current_date = datetime(year=2020, month=9, day=30)

    # check if filters on period are activated
    periods = filters.get("Periode")
    if periods.get("options") != []:
        # periods are selected, so only get those observations
        # get the max and min range of the period
        begin_date = util.get_period_range(periods.get("options"))[0]
    else:
        # if no filters are selected get the latest week
        begin_date = current_date - timedelta(7)

    # retrieve all relevant observations from the Observations table
    observation_set = list(Observations.objects.filter(period_end__gte=begin_date)
                                               .order_by('-period_end', '-relevance'))

    # get the initial observation and pass it into the chosen_observs (history)
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
    chosen_observs = [first_observ]

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

    for x in range(0, 10):
        determinator = Determinator(observation_set, chosen_observs)
        determinator.calculate_new_situational_relevance()

        # get the newly chosen observation, save it and restart the process
        new_observ = determinator.get_highest_relevance()
        chosen_observs.append(new_observ)
        observation_set = determinator.all_observations

    # set the chosen observations to the planner
    planner = Planner(chosen_observs)
    planner.plan()

    # set the planned observations into the realiser
    realiser = Realiser(planner.observations)
    realiser.realise()

    # select all the id's, corresponding situational relevances and the sentences of the to be article
    observs_id = []
    sit_relev = []
    sentences = []

    for observ in realiser.observs:
        observs_id.append(observ.observ_id)
        sit_relev.append(observ.relevance2)
        sentences.append(observ.observation_new)

        print(observ.year, observ.week_number, observ.day_number, observ.pattern, observ.observation_new)

    # build the article by appending all sentences
    content = " ".join(sentences)

    # get the meta data and save it into the article
    meta = {}
    meta["manual"] = filters.get("manual")
    meta["filters"] = {}
    meta["observs"] = observs_id
    meta["sit_relev"] = sit_relev

    for x in ["Sector", "Periode"]:
        selection = filters.get(x)
        print(selection)
        if (selection.get("total") != len(selection.get("options"))) and (selection.get("options") != []):
            meta["filters"][x] = selection.get("options")
        else:
            meta["filters"][x] = "Alles"

    # select the focus of the image
    comps_focus = []
    sector_focus = []
    for observ in planner.observations:
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
    article.title = f"Beurs update {datetime.now().strftime('%d %b')}"
    article.top_image = retrieve_url
    article.content = content
    article.date = datetime.now()
    article.AI_version = AI_VERSION
    article.meta_data = meta
    if bot:
        article.author = "nieuwsbot"
    else:
        article.author = user_name
    article.save()

    return article.id


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
    print(comps_focus)
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


# TODO format this function!!
def generate_article_photo(components: list, sector_focus: str = None):
    """[summary]

    Args:
        components (list): A list of the components that have to be in the photo of the article (max 2)
        sector_focus (str, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
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

    # cv2.imshow('dst', new_image)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     cv2.destroyAllWindows()
    return new_image


def test_photo():
    # TODO throw away this method when tested and in production
    comps = ["BAM Groep Koninklijke", "SIGNIFY NV"]
    # comps = ["SIGNIFY NV", "Flow Traders"]
    comps = ["BAM Groep Koninklijke", "Intertrust"]
    sector = "Bouw"
    generate_article_photo(comps, sector_focus=sector)


def testing_find_observs():
    """Small function for testing and development purposes.
    """
    # period_begin = datetime(year=2020, month=7, day=14)
    period_begin = datetime(year=2020, month=9, day=16)
    period_end = datetime(year=2020, month=9, day=17)

    find_new_observations(period_begin, period_end, to_prompt=True, overwrite=True)


def find_new_observations(period_begin: datetime, period_end: datetime, overwrite=False, to_db=False, to_prompt=False, to_list=False):
    """Runs all functions to find observations, collects the observations and deals with them in the proper way.

    Args:
        overwrite (bool, optional) : Decide whether duplicate observations are handled. Defaults to False
        to_db (bool, optional): Decide whether the new observations are to be written into the database. Defaults to False.
        to_prompt (bool, optional): Decide whether the new observations are to be written to the prompt. Defaults to False.
        to_list (bool, optional): Decide whether the new observations are to be returned as a list of observations. Defaults to False.
    """
    all_observations = []

    all_observations.extend(run_period_observations(period_begin, period_end, overwrite))
    all_observations.extend(run_week_observations(period_begin, period_end, overwrite))
    all_observations.extend(run_trend_observations(period_end, 14, overwrite))

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


def run_period_observations(period_begin, period_end, overwrite):
    """
    Check if the given period has already been observed,
    if not get all the relevant data and run the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period
        overwrite (bool): If duplicate observations can be made

    Returns:
        list: A list with the observations found
    """
    observs = []
    # check if this period in observations has already been asked before
    observ_exists = Observations.objects.filter(period_begin=period_begin).filter(period_end=period_end).exists()
    if not observ_exists or overwrite:
        # retrieve all data over the stocks in this period
        data = Stocks.objects.filter(date__range=(period_begin, period_end))
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


def run_week_observations(period_begin, period_end, overwrite):
    """
    Check if a whole week has already been observed,
    if not gets all the weeks in the range of the beginning and the end of the period and runs the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period
        overwrite (bool): If duplicate observations can be made

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

    if overwrite:
        open_periods = all_periods
    else:
        # check for every week if there is already an observation made
        open_periods = [x for x in all_periods if not Observations.objects.filter(pattern="week")
                                                                          .filter(period_begin=x[0])
                                                                          .filter(period_end=x[1]).exists()]

    # run a new observation if the week hasn't been observerd
    if len(open_periods) > 0:
        for period in open_periods:
            # retrieve all data over the stocks in this period
            data = Stocks.objects.filter(date__range=period)
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


def run_trend_observations(period_end, delta_days, overwrite):
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

    if overwrite:
        observs.extend(analyse.observations)
    else:
        observs.extend([x for x in analyse.observations if not Observations.objects.filter(pattern=x.pattern)
                                                                                   .filter(serie=x.serie)
                                                                                   .filter(period_end=x.period_end)
                                                                                   .filter(period_end=x.period_end).exists()])

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
